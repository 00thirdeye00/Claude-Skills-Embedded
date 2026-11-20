# Shared data patterns for ISRs and tasks

Examples use CMSIS names (`__get_PRIMASK`, `__disable_irq`, `__set_PRIMASK`, `__DMB`). Adapt to your toolchain.

## Contents
- Critical section that nests
- Single-producer single-consumer ring buffer
- Double buffer
- Flag and deferred-work handoff
- Barriers: when you need them
- Interrupt latency budget

## Critical section that nests

```c
static inline uint32_t cs_enter(void) { uint32_t m = __get_PRIMASK(); __disable_irq(); return m; }
static inline void     cs_exit(uint32_t m) { __set_PRIMASK(m); }

uint32_t m = cs_enter();
shared.count++;            /* read-modify-write is now safe against ISRs */
cs_exit(m);
```

Keep the masked region to a few instructions. On Cortex-M3 and up, `BASEPRI` masks only interrupts at or below a chosen priority, which keeps urgent interrupts running; RTOS ports use this.

## Single-producer single-consumer ring buffer

Safe with exactly one writer (for example an ISR) and one reader (a task or main loop) on a single core. Each index is written by one side only.

```c
#define RB_SIZE 64u                       /* power of two */
typedef struct {
    uint8_t buf[RB_SIZE];
    volatile uint32_t head;               /* written by the producer only */
    volatile uint32_t tail;               /* written by the consumer only */
} rb_t;

static inline bool rb_put(rb_t *r, uint8_t v) {       /* producer */
    uint32_t h = r->head;
    if (((h + 1u) & (RB_SIZE - 1u)) == r->tail) return false;   /* full */
    r->buf[h] = v;
    __asm volatile ("" ::: "memory");                 /* data before index */
    r->head = (h + 1u) & (RB_SIZE - 1u);
    return true;
}

static inline bool rb_get(rb_t *r, uint8_t *v) {      /* consumer */
    uint32_t t = r->tail;
    if (t == r->head) return false;                   /* empty */
    *v = r->buf[t];
    __asm volatile ("" ::: "memory");                 /* data before index */
    r->tail = (t + 1u) & (RB_SIZE - 1u);
    return true;
}
```

Usable capacity is `RB_SIZE - 1`. On a single core, a compiler barrier orders the accesses. If a second bus master (DMA, another core) reads or writes the buffer, also account for caches and hardware ordering.

## Double buffer

The producer (ISR or DMA) fills buffer A while the consumer processes buffer B. On completion the producer flips a `volatile` index and sets a ready flag. The consumer must finish before the producer wraps back; check this with a counter that detects overrun and report it rather than silently dropping data.

## Flag and deferred-work handoff

```c
static volatile bool g_rx_ready;          /* set in ISR, cleared by main loop */

void USARTx_IRQHandler(void) { /* read data, clear source */ g_rx_ready = true; }

void main_loop(void) {
    if (g_rx_ready) { g_rx_ready = false; process(); }   /* single writer per transition */
}
```

If the ISR can fire again between the check and the clear, a pulse can be lost. Use a counter, a queue, or an RTOS notification when events must not be merged.

## Barriers: when you need them

- **Compiler barrier** (`asm volatile("" ::: "memory")`): between plain-memory writes and the index or flag that publishes them.
- **`__DMB()`**: ordering between memory accesses seen by other masters, for example DMA descriptors written before a start bit.
- **`__DSB()` then `__ISB()`**: after changing `VTOR`, enabling an interrupt that must take effect immediately, or before `WFI` when a pending write must complete.
- Peripheral registers are device memory and stay ordered with respect to each other, but a write may still be buffered; read back when the effect must be visible before the next instruction.

## Interrupt latency budget

Latency to the first handler instruction is roughly: longest interrupts-masked region, plus exception entry (about 12 cycles on Cortex-M3 and M4 with zero-wait-state memory, about 15 to 16 on M0 and M0+), plus any wait states, plus the time to finish a multi-cycle instruction. Higher-priority interrupts that preempt add their own runtime. Measure with a GPIO toggle on an oscilloscope or the DWT cycle counter, and compare against the deadline with margin.
