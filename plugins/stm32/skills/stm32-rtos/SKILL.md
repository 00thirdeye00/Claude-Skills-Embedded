---
name: stm32-rtos
description: Set up or troubleshoot FreeRTOS, Zephyr, ThreadX, or RT-Thread on an STM32: priorities, HAL timebase, task patterns, overlays, Kconfig.
argument-hint: "<RTOS, part, setup question, config, or the symptom>"
disable-model-invocation: true
---

# /stm32:stm32-rtos

Set up and troubleshoot FreeRTOS, Zephyr, ThreadX, or RT-Thread on an STM32.

## Workflow

1. Identify the RTOS and version, the part and core, the wrapper layer (native FreeRTOS, CMSIS-RTOS v2, Zephyr, ThreadX, RT-Thread), and the symptom or configuration. Ask only for what is missing.
2. Load the matching reference below.
3. For FreeRTOS: match the port to the core, set the interrupt priority model, move the HAL timebase off the RTOS tick, then check stacks, heap, and the ISR-to-task handoff.
4. For Zephyr: build a known sample first, describe hardware in an overlay, select features in Kconfig, and check `device_is_ready()`.
5. List items to confirm against the documentation of the exact RTOS version.

## References

| Topic | Load |
|---|---|
| FreeRTOSConfig, priorities, handlers, HAL timebase, heap, stacks, tickless idle | `references/freertosconfig-stm32.md` |
| FreeRTOS patterns: ISR to task, DMA with queues, bus locking, periodic tasks | `references/freertos-patterns.md` |
| Zephyr on STM32: west, overlays, clocks, Kconfig, drivers, MCUboot | `references/zephyr-stm32.md` |
| ThreadX on STM32 | `references/threadx-stm32.md` |
| RT-Thread on STM32 | `references/rtthread-stm32.md` |

## Rules

- Never call a non-ISR API from an interrupt, and no RTOS API from an interrupt more urgent than the maximum syscall priority.
- State stack-size units (words in native FreeRTOS, bytes in CMSIS-RTOS v2 and Zephyr).
- RTOS names, defaults, and board names change between versions; verify against the version in use.
- For general task architecture and schedulability use `/embedded-core:embedded-rtos-concepts`.
- With architecture documents, each task, queue, and mutex is created and owned by one module and listed in the resource map; update the documents with `/stm32:stm32-architecture` after changes.
