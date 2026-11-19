---
name: stm32-debug
description: Structured debugging for STM32 firmware — reproduce, isolate, diagnose, fix. Use when an STM32 project hits a HardFault, BusFault, UsageFault, or MemManage fault, hangs, resets in a loop, or lands in Default_Handler; when a peripheral does nothing (clock, pin-mux, DMA not firing, interrupt never arrives); when an RTOS task crashes or overflows its stack; or when behavior differs between debugger and standalone, debug and release builds, or STM32 families. Trigger with "HardFault", "CFSR", "stuck in Default_Handler", "DMA not working", "I2C hangs", "works under the debugger but not standalone", "FreeRTOS assert on interrupt priority".
argument-hint: "<symptom, fault register values, or stacked register dump>"
---

# /stm32:stm32-debug

Run a structured debugging session for STM32 firmware: reproduce, isolate, diagnose, fix.

## Usage

```
/stm32:stm32-debug $ARGUMENTS
```

If no symptom is given, ask what the device does versus what it should do.

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                         STM32 DEBUG                               │
├─────────────────────────────────────────────────────────────────┤
│  Step 1: IDENTIFY THE TARGET                                      │
│  ✓ Family, core (M0/M0+, M3, M4, M7, M33), HAL/LL/bare-metal     │
│  ✓ RTOS (FreeRTOS, Zephyr, none), build type, bootloader         │
│                                                                    │
│  Step 2: CLASSIFY THE SYMPTOM                                     │
│  ✓ Fault, hang, silent peripheral, reset loop, debug-only bug    │
│                                                                    │
│  Step 3: CAPTURE EVIDENCE                                         │
│  ✓ Fault registers, stacked PC/LR, SP, map file, raw values      │
│                                                                    │
│  Step 4: ISOLATE AND DIAGNOSE                                     │
│  ✓ One hypothesis at a time, each with a confirming check        │
│                                                                    │
│  Step 5: FIX AND PREVENT                                          │
│  ✓ Root cause, minimal fix, regression guard                     │
└─────────────────────────────────────────────────────────────────┘
```

## Step 1: Identify the target

Collect only what is missing from the conversation:

- Part number or family (for example STM32F407, STM32G071, STM32H743, STM32U575). The core decides which fault registers exist.
- Software stack: HAL, LL, register-level, or Zephyr; CubeMX-generated or hand-written.
- RTOS and version, if any.
- Whether a bootloader is in use, and the build flags (optimization level, FPU ABI).

Load `references/family-notes.md` to map the family to its core, FPU, cache, and fault-register availability.

## Step 2: Classify the symptom

| Symptom | First suspects | Load |
|---|---|---|
| Lands in `HardFault_Handler` (or another fault handler) | Decode CFSR/HFSR, stacked PC, fault address | `references/hardfault-decode.md` |
| Stuck in `Default_Handler` or an ISR re-enters forever | Missing or misnamed handler, interrupt flag never cleared | `references/common-causes.md` § Interrupts |
| Peripheral does nothing | RCC clock, kernel clock mux, GPIO alternate function, power domain | `references/common-causes.md` § Peripheral silent |
| DMA transfer never happens or data is wrong | Request mapping, memory region not DMA-reachable, cache coherency | `references/common-causes.md` § DMA |
| Hangs inside HAL calls or `HAL_Delay` | SysTick priority, HAL tick source with an RTOS, timeout handling | `references/common-causes.md` § HAL |
| Hangs or resets after raising clock speed | Flash wait states, PLL lock, voltage scaling | `references/common-causes.md` § Clock and flash |
| Works under the debugger, fails standalone (or the reverse) | Debug freeze bits, low-power debug, BOOT pins, option bytes, uninitialized data | `references/common-causes.md` § Debug versus standalone |
| Works at `-O0`, fails optimized | Missing `volatile`, data races, undefined behavior, stack size | `references/common-causes.md` § Debug versus standalone |
| RTOS assert, task crash, random corruption | Stack overflow, interrupt priority versus RTOS limit, heap exhaustion | `references/common-causes.md` § RTOS |
| Reset loop | Watchdog, brown-out, clock security, bad vector table after a bootloader jump | `references/common-causes.md` § Debug versus standalone |

When the symptom matches several rows, start with the cheapest check.

## Step 3: Capture evidence

Ask for raw values, not paraphrases. Useful evidence:

- `CFSR`, `HFSR`, `MMFAR`, `BFAR` and the stacked `PC`, `LR`, `xPSR` (see `references/hardfault-decode.md` for a handler that captures them).
- Resolve addresses to source with `arm-none-eabi-addr2line -e <elf> -f -p -i <address>`.
- Inspect the faulting instruction with `arm-none-eabi-objdump -d -S <elf>` around the stacked PC.
- Check section sizes and stack/heap placement with `arm-none-eabi-size` and the linker map file.
- Peripheral register dumps taken at the point of failure, not after a reset.

If the user pastes a fault dump or register values, decode them with the references first, then ask follow-up questions.

## Step 4: Isolate and diagnose

1. Check recent changes first (new peripheral, clock change, linker script edit, library update).
2. Bisect: disable peripherals or tasks one at a time, lower the clock, switch to `-O0`, or run a minimal project.
3. State each hypothesis together with the one check that would confirm or refute it. Run the checks one at a time.
4. Trace the failing code path to the root cause, not only the instruction that faulted.

## Step 5: Fix and prevent

Propose the smallest fix that addresses the root cause. State side effects and edge cases. Suggest a guard that would have caught the problem earlier (an assert, a stack-overflow hook, an MPU guard region, a unit or hardware-in-the-loop test).

## Output

```markdown
## Debug Report: [issue summary]

### Target
- **Part / core**: [family, core, FPU, cache]
- **Stack**: [HAL/LL/bare-metal, RTOS, build type]

### Evidence
- [fault registers, stacked PC/LR, register dumps, symptoms]

### Root Cause
[why it happens, with the chain from symptom to cause]

### Fix
[code or configuration change]

### Verification
- [how to confirm the fix on hardware]

### Prevention
- [assert, hook, test, or guard to add]
```

## Rules

- Decode before asking: use the reference tables on any pasted register value.
- Distinguish core-level facts (Arm architecture, stable) from family-level facts (reference manual, errata). For family-level register names, bit positions, and peripheral behavior, tell the user to confirm against the reference manual, datasheet, and errata sheet for the exact part and silicon revision.
- Never present a guess as the root cause. Say which check is still needed.
- Keep the fault handler in the firmware after the fix; do not replace it with an empty loop.

## If Connectors Available

If **~~source control** is connected:
- Identify recent commits and pull requests that touched the clock setup, linker script, interrupt handlers, or drivers involved.

If **~~project tracker** is connected:
- Search for related bug reports and create a ticket once the root cause is known.

If **~~knowledge base** is connected:
- Look up the reference manual excerpt, errata sheet, or team notes for the part in question.

## Tips

1. **Paste exact values**: hex register dumps beat descriptions.
2. **Say what changed**: a new clock setting, library bump, or compiler flag is the top suspect.
3. **Mention the family early**: Cortex-M0/M0+ parts (F0, G0, L0, C0) have no CFSR; the decoding path is different.
4. **Note the debug context**: whether the failure happens only with or without a debugger attached narrows the search quickly.
5. **Go deeper per peripheral**: use the matching `stm32-<peripheral>` skill (for example `stm32-i2c` or `stm32-dma`) once the failing peripheral is known. For platform-independent methods and instrumentation, use `/embedded-core:embedded-debug` if installed.
