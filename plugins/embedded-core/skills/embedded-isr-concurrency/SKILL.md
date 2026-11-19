---
name: embedded-isr-concurrency
description: Rules and patterns for interrupt service routines and shared data in bare-metal and RTOS firmware on any MCU. Use when writing or reviewing an ISR, sharing data between an ISR and main loop or task, deciding between volatile, critical sections, atomics, and lock-free buffers, handling race conditions, or estimating interrupt latency. Trigger with "is this ISR safe", "race condition", "volatile vs atomic", "shared variable between interrupt and task", "ring buffer from ISR", "critical section", "interrupt latency".
argument-hint: "<code, design question, or symptom involving interrupts and shared data>"
---

# /embedded-core:embedded-isr-concurrency

Design or review interrupt handling and shared-data access so it is correct, bounded in time, and free of races.

## Usage

```
/embedded-core:embedded-isr-concurrency $ARGUMENTS
```

If no code or design is given, ask what the ISR does, what data it shares, and who consumes it.

## Workflow

1. **Identify the actors.** List every ISR, task, and DMA engine that touches the data, with priorities. Note the core (Cortex-M0/M0+ lacks exclusive-access instructions; M3 and up have them).
2. **Check ISR rules** (below) for every handler.
3. **Classify each shared object** and pick a mechanism with the table below.
4. **Check the time budget.** Worst-case masked time plus ISR runtime must fit the tightest deadline.
5. **Report** using the output template.

## ISR rules

- Keep the handler short: read hardware, clear the source, hand off, return.
- Never block, wait on a flag, call `malloc`/`free`, or call `printf` and other non-reentrant or slow library functions.
- Clear the interrupt source in the order the device documentation requires. After clearing a flag in a peripheral, read the register back (or issue a barrier) when the handler returns immediately, so write buffering cannot cause a spurious re-entry.
- In an RTOS, call only the ISR-safe API variants and only from interrupts at or below the RTOS's maximum syscall priority.
- Avoid floating point in ISRs unless the FPU context cost is accounted for.
- Give every ISR a documented worst-case execution time.

## Choosing a mechanism

| Shared object | Mechanism |
|---|---|
| One flag or 32-bit aligned word, one writer | `volatile` is enough on Cortex-M; the access is a single instruction |
| Multi-word struct, 64-bit value, read-modify-write (`counter++`) | Critical section, or atomics on cores that have exclusive access |
| Byte stream, one producer and one consumer | Single-producer single-consumer ring buffer (see `references/shared-data-patterns.md`) |
| Block of samples filled by DMA or ISR | Double (ping-pong) buffer with a swap flag |
| Many producers or consumers | RTOS queue or mutex, not hand-rolled lock-free code |
| ISR signals a task | Semaphore, task notification, or queue send from ISR |

`volatile` forces the compiler to perform each access. It does not make a sequence of accesses atomic and does not order accesses against other bus masters.

## Output

```markdown
## Concurrency Review: [component]

### Actors
- [ISR/task/DMA, priority, what it touches]

### Findings
| # | Severity | Location | Issue | Fix |
|---|---|---|---|---|

### Time budget
- Worst-case ISR time: [value]; max interrupts-masked time: [value]; tightest deadline: [value]

### Recommended mechanism
[per shared object]
```

## Rules

- Prefer the simplest correct mechanism. Do not propose lock-free code where a short critical section is clearly cheap enough.
- State the core and compiler assumptions behind any atomicity claim.
- Save and restore `PRIMASK` (or `BASEPRI`) rather than blindly re-enabling interrupts, so critical sections nest.

## Tips

1. **Share the handler and the consumer** together; races live in the pair, not in either alone.
2. **Say which core**: atomicity and available instructions differ between M0/M0+ and M3 and up.
3. **Measure** ISR time with a GPIO toggle or the cycle counter before trusting estimates.
