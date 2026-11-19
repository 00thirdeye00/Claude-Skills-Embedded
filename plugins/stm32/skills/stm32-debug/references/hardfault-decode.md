# Decoding Cortex-M faults on STM32

Core-level facts below come from the Arm architecture (ARMv6-M, ARMv7-M, ARMv8-M) and are stable across vendors. Confirm details for your core in the Arm Architecture Reference Manual and the core's Technical Reference Manual. Family-level behavior (what a specific peripheral does on a bad access) comes from the STM32 reference manual and errata.

## Contents
- Which fault registers exist
- Capture the fault context
- Fault status registers
- Reading the stacked registers
- Fault address: what it means on STM32
- Quick triage order

## Which fault registers exist

| Core | Fault model |
|---|---|
| Cortex-M0 / M0+ (ARMv6-M) | HardFault only. No CFSR, HFSR, MMFAR, or BFAR. Use the stacked PC and LR plus the core registers. |
| Cortex-M3 / M4 / M7 (ARMv7-M) | HardFault plus configurable MemManage, BusFault, and UsageFault. CFSR, HFSR, MMFAR, BFAR available. |
| Cortex-M33 (ARMv8-M Mainline) | Same as ARMv7-M plus stack-limit faults and, with TrustZone, secure fault registers (SFSR, SFAR). |

Configurable faults escalate to HardFault when their handler is disabled (SHCSR enable bits) or cannot preempt the running priority. When `HFSR.FORCED` is set, the real cause is in `CFSR`.

## Capture the fault context

Install a handler that picks the stack in use at the time of the fault and passes it to C. Use the handler that matches the core.

Cortex-M3 / M4 / M7 / M33 (GCC, Thumb-2):

```c
#include "stm32xxxx.h"   /* your family's CMSIS device header */

__attribute__((naked)) void HardFault_Handler(void)
{
    __asm volatile (
        "tst lr, #4        \n"   /* EXC_RETURN bit 2: 0 = MSP, 1 = PSP */
        "ite eq            \n"
        "mrseq r0, msp     \n"
        "mrsne r0, psp     \n"
        "mov r1, lr        \n"   /* pass EXC_RETURN as well */
        "b hard_fault_c    \n"
    );
}

void hard_fault_c(uint32_t *frame, uint32_t exc_return)
{
    volatile uint32_t r0 = frame[0], r1 = frame[1], r2 = frame[2], r3 = frame[3];
    volatile uint32_t r12 = frame[4];
    volatile uint32_t lr  = frame[5];   /* LR at the time of the fault (the caller) */
    volatile uint32_t pc  = frame[6];   /* instruction that faulted (precise faults) */
    volatile uint32_t psr = frame[7];

    volatile uint32_t cfsr  = SCB->CFSR;
    volatile uint32_t hfsr  = SCB->HFSR;
    volatile uint32_t mmfar = SCB->MMFAR;
    volatile uint32_t bfar  = SCB->BFAR;
    (void)r0; (void)r1; (void)r2; (void)r3; (void)r12;
    (void)lr; (void)pc; (void)psr; (void)cfsr; (void)hfsr;
    (void)mmfar; (void)bfar; (void)exc_return;

    __BKPT(0);                          /* inspect the locals under the debugger */
    for (;;) { }                        /* or log to a retained buffer and reset */
}
```

Cortex-M0 / M0+ (Thumb-1 has no `IT` instruction and no fault status registers):

```c
__attribute__((naked)) void HardFault_Handler(void)
{
    __asm volatile (
        "movs r0, #4            \n"
        "mov  r1, lr            \n"   /* EXC_RETURN, passed as second argument */
        "tst  r0, r1            \n"
        "beq  1f                \n"
        "mrs  r0, psp           \n"
        "b    2f                \n"
        "1:                     \n"
        "mrs  r0, msp           \n"
        "2:                     \n"
        "ldr  r2, =hard_fault_c \n"
        "bx   r2                \n"
    );
}

void hard_fault_c(uint32_t *frame, uint32_t exc_return)
{
    volatile uint32_t pc = frame[6], lr = frame[5], psr = frame[7];
    (void)pc; (void)lr; (void)psr; (void)exc_return;
    __BKPT(0);
    for (;;) { }
}
```

Notes:
- The basic exception frame is `R0, R1, R2, R3, R12, LR, PC, xPSR` at word offsets 0 to 7. This holds with or without an FPU extended frame; the FPU registers follow after these eight words.
- If `xPSR` bit 9 is set, the hardware inserted one padding word for 8-byte stack alignment. It does not change the offsets above.
- `LR` inside the handler holds `EXC_RETURN`. The `LR` in the frame is the caller's return address. Resolve both to source.
- On Cortex-M33 with TrustZone the `EXC_RETURN` encoding and stack selection differ (secure versus non-secure stacks). Use the Arm Architecture Reference Manual for ARMv8-M, not the snippet above.

## Fault status registers (ARMv7-M and ARMv8-M Mainline)

`CFSR` (0xE000ED28) combines three fields: MMFSR (bits 7:0), BFSR (bits 15:8), UFSR (bits 31:16).

### MemManage (MMFSR, CFSR bits 7:0)

| Bit | Name | Meaning | Typical cause |
|---|---|---|---|
| 0 | IACCVIOL | Instruction fetch violated MPU or execute-never rules | Jumped into a non-executable region; bad function pointer |
| 1 | DACCVIOL | Data access violated MPU rules | MPU guard region hit (stack guard, NULL guard); wild pointer |
| 3 | MUNSTKERR | MPU fault while unstacking on exception return | Stack corrupted or overflowed inside the ISR |
| 4 | MSTKERR | MPU fault while stacking on exception entry | Stack overflow into a protected region |
| 5 | MLSPERR | MPU fault during lazy FP state save (FPU cores) | Stack overflow with FPU context |
| 7 | MMARVALID | `MMFAR` holds the faulting address | Read `MMFAR` only when set |

### BusFault (BFSR, CFSR bits 15:8)

| Bit | Name | Meaning | Typical cause |
|---|---|---|---|
| 8 | IBUSERR | Bus error on instruction fetch | Jump to an unmapped or unpowered address |
| 9 | PRECISERR | Precise data bus error; stacked PC is the faulting instruction | Access to an invalid or inaccessible address |
| 10 | IMPRECISERR | Imprecise data bus error; stacked PC may be later than the cause | Buffered write to an invalid address; `BFAR` is not valid |
| 11 | UNSTKERR | Bus error while unstacking | Corrupted or invalid stack pointer |
| 12 | STKERR | Bus error while stacking | Stack pointer outside valid memory |
| 13 | LSPERR | Bus error during lazy FP state save | Stack pointer invalid with FPU context |
| 15 | BFARVALID | `BFAR` holds the faulting address | Read `BFAR` only when set |

For `IMPRECISERR`, the write buffer delays the error. To make the fault precise while debugging, disable the default write buffer on Cortex-M3/M4 by setting `ACTLR.DISDEFWBUF` (`SCnSCB->ACTLR |= SCnSCB_ACTLR_DISDEFWBUF_Msk`). Other cores may not offer this; check the core's Technical Reference Manual. Expect a performance cost, so keep it out of release builds.

### UsageFault (UFSR, CFSR bits 31:16)

| Bit | Name | Meaning | Typical cause |
|---|---|---|---|
| 16 | UNDEFINSTR | Undefined instruction executed | Executing data or erased flash; wrong core or FPU build flags |
| 17 | INVSTATE | Invalid EPSR state, usually Thumb bit clear | Function pointer or return address with bit 0 clear; ARM-mode address |
| 18 | INVPC | Invalid exception return value | Corrupted stack or `EXC_RETURN` in an ISR |
| 19 | NOCP | Coprocessor instruction with the coprocessor disabled | FPU instruction while CP10/CP11 are not enabled |
| 20 | STKOF | Stack overflow detected by the stack limit (ARMv8-M only) | Task or main stack too small |
| 24 | UNALIGNED | Unaligned access trapped | Unaligned `LDM`/`STM`/`LDRD`, or `CCR.UNALIGN_TRP` set |
| 25 | DIVBYZERO | Divide by zero trapped | `CCR.DIV_0_TRP` set and a zero divisor |

`NOCP` on a part with an FPU and a hard-float build means the FPU was never enabled. CMSIS `SystemInit()` enables it (`SCB->CPACR |= 0xF << 20`) when the device header defines the FPU as present and used. A custom startup that skips `SystemInit()` is the usual culprit.

### HardFault (HFSR, 0xE000ED2C)

| Bit | Name | Meaning |
|---|---|---|
| 1 | VECTTBL | Bus fault reading the vector table during exception processing |
| 30 | FORCED | A configurable fault escalated; read `CFSR` for the cause |
| 31 | DEBUGEVT | Debug event while debug is disabled |

Cortex-M0/M0+ cores have no configurable faults, so all faults arrive as HardFault without status registers. Work from the stacked PC and the instruction at that address.

## Reading the stacked registers

1. Resolve the stacked `PC` to a source line: `arm-none-eabi-addr2line -e fw.elf -f -p -i 0x<PC>`.
2. Disassemble around it: `arm-none-eabi-objdump -d -S fw.elf | less`, then search for the address.
3. Check which register held the bad address (the faulting instruction names it) and read its value from the frame (`R0` to `R3`, `R12`) or recompute it.
4. Resolve the stacked `LR` to find the caller.
5. For `IMPRECISERR`, expect the real cause a few instructions earlier than `PC`. Look at recent stores to peripherals or memory.
6. Compare the stack pointer (`frame` address) with the task or main stack bounds in the map file. A frame address outside them means a stack overflow.

## Fault address: what it means on STM32

Use the Arm memory map, then confirm the exact ranges for the part in the reference manual.

| Address range | Region | If it faulted here |
|---|---|---|
| 0x0000_0000 to 0x1FFF_FFFF | Code (flash, boot alias, system memory, some TCM or CCM) | Executing or reading an unmapped part of the code region |
| 0x2000_0000 to 0x3FFF_FFFF | SRAM | Past the end of SRAM, or an unpowered or ECC-protected bank not initialized |
| 0x4000_0000 to 0x5FFF_FFFF | Peripherals | Peripheral clock off, peripheral absent on this part, wrong access width |
| 0x6000_0000 to 0x9FFF_FFFF | External memory (FMC, FSMC, OctoSPI) | External memory not initialized |
| 0xE000_0000 to 0xE00F_FFFF | Private peripheral bus (SCB, NVIC, SysTick, debug) | Privilege violation from unprivileged code |

Peripheral accesses with the bus clock disabled behave differently by series. Many parts return zero and ignore writes without a fault, while others raise a bus error. If a peripheral register misbehaves, check the RCC enable bits first, whether or not a fault occurred.

A NULL pointer dereference often does not fault on STM32, because address 0 is aliased to flash (or another memory, depending on boot configuration). Reads quietly succeed and the program corrupts state later. An MPU region covering address 0 with no access turns that into a precise `DACCVIOL`, where the part has an MPU.

## Quick triage order

1. Is `HFSR.FORCED` set? If so, decode `CFSR`. If not and `VECTTBL` is set, the vector table is unreadable (bad `VTOR`).
2. Is the stack pointer inside the expected stack? If not, treat it as a stack overflow first.
3. `INVSTATE` or `INVPC`: suspect a corrupted return address, a bad function pointer, or a wrong `EXC_RETURN`.
4. `PRECISERR` with `BFARVALID`: inspect `BFAR` against the memory map.
5. `IMPRECISERR`: disable the write buffer (where available) and reproduce.
6. `UNDEFINSTR` or `NOCP`: check build flags (`-mcpu`, `-mfpu`, `-mfloat-abi`) against the part, and FPU enable.

Verify register addresses and bit positions against the Arm Architecture Reference Manual and the core Technical Reference Manual for your core, and the STM32 reference manual for family-specific behavior.
