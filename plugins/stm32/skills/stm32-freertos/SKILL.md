---
name: stm32-freertos
description: Integrate and debug FreeRTOS on STM32 (with or without the CMSIS-RTOS wrapper and CubeMX): FreeRTOSConfig values, interrupt priority rules for Cortex-M, port selection, HAL timebase separate from the RTOS tick, heap schemes, stack sizing and overflow detection, ISR-to-task handoff, DMA with queues and task notifications, shared peripheral locking, and tickless idle with STM32 low-power modes. Use when starting an STM32 FreeRTOS project, hitting configASSERT on interrupt priority, hard faults in tasks, scheduler not starting, or tasks starving. Trigger with "FreeRTOS on STM32", "FreeRTOSConfig", "configMAX_SYSCALL_INTERRUPT_PRIORITY", "xQueueSendFromISR", "FreeRTOS hard fault", "CMSIS-RTOS v2", "HAL tick with FreeRTOS", "tickless idle STM32".
argument-hint: "<project setup, task design, FreeRTOSConfig, or the symptom>"
---

# /stm32:stm32-freertos

Set up, design, and troubleshoot FreeRTOS on STM32 devices.

## Usage

```
/stm32:stm32-freertos $ARGUMENTS
```

If details are missing, ask for the part and core, the FreeRTOS version, whether the CMSIS-RTOS wrapper is used, the number of priority bits, the HAL tick source, and the symptom or FreeRTOSConfig.

## Workflow

1. **Match the port to the core** (Cortex-M0 or M0+, M3, M4 with FPU, M7, M33 with or without TrustZone).
2. **Set the interrupt priority model**: lowest priority for the kernel, a maximum syscall priority for ISRs that call the API, one priority grouping with all bits as preemption (see `references/freertosconfig-stm32.md`).
3. **Separate the timebases**: give the RTOS the core tick and move the HAL tick to a spare timer.
4. **Design tasks and communication** with the `embedded-rtos-concepts` guidance if installed; otherwise use the patterns in `references/freertos-patterns.md`.
5. **Size stacks and heap**, enable overflow detection, malloc-failed hook, and assert.
6. **Check peripherals under the RTOS**: lock shared buses, use callbacks that signal tasks, and keep blocking calls out of ISRs.
7. **Verify** with run-time statistics, stack high-water marks, and a deliberate overflow or priority test.

## Output

```markdown
## FreeRTOS Plan: [project]

### Configuration
| Setting | Value | Reason |
|---|---|---|

### Interrupt priorities
| Source | Priority | Calls RTOS API? |
|---|---|---|

### Tasks
| Task | Priority | Stack | Trigger | Communication |
|---|---|---|---|---|

### Risks and checks
- [..]
```

## Rules

- Never call a non-ISR API from an interrupt, and never call any API from an interrupt above the maximum syscall priority.
- State the units of stack sizes (words in the native API, bytes in the CMSIS-RTOS v2 wrapper).
- Take configuration names and defaults from the FreeRTOS version in use; they change between releases.

## Tips

1. **`configASSERT` in the priority check** means an ISR with a numerically lower priority than allowed calls the RTOS API.
2. **A fault at scheduler start** is often the wrong port, a too-small main stack, or interrupts enabled too early.
3. **Starvation** often comes from a high-priority task that never blocks.
