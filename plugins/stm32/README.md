# stm32 plugin

Skills for developing STM32 firmware with Claude: debugging, design, code review, driver bring-up, low power, bootloaders and OTA updates, release checks, ten peripheral skills, and FreeRTOS and Zephyr integration, across STM32 families.

Companion plugin: `embedded-core` (platform-independent theory and checklists). Every skill here also carries enough inline guidance to work when `embedded-core` is not installed.

## Skills

| Group | Skill | Use for |
|---|---|---|
| Workflow | `stm32-design` | Part selection, clock tree, pin and DMA plan, memory map, interrupt priorities, budgets |
| Workflow | `stm32-review` | STM32-specific code review: HAL/LL misuse, clocks, DMA and cache, priorities, flash and option bytes |
| Workflow | `stm32-debug` | HardFault decoding, hangs, silent peripherals, HAL and RTOS pitfalls, debug versus standalone |
| Workflow | `stm32-driver-bringup` | Datasheet to tested driver, bus port layering, bring-up order |
| Workflow | `stm32-power` | Sleep, Stop, Standby, wake sources, tickless idle, current budget and measurement |
| Workflow | `stm32-bootloader-ota` | System bootloader, DFU, custom bootloader handover, A/B slots, MCUboot |
| Workflow | `stm32-release` | Option bytes, read-out protection policy, image checks, production programming |
| Peripheral | `stm32-gpio-exti` | Pin modes, EXTI lines, debouncing, wake-up |
| Peripheral | `stm32-uart` | Baud and clocks, DMA with idle line, errors, RS-485, LPUART |
| Peripheral | `stm32-i2c` | Timing, transfers, errors, bus recovery, slave mode |
| Peripheral | `stm32-spi` | Modes, prescaler, chip-select, DMA, slave mode |
| Peripheral | `stm32-can` | bxCAN and FDCAN bit timing, filters, bus-off, CAN FD |
| Peripheral | `stm32-usb` | Clock, VBUS and pull-up, CDC and other classes, enumeration failures |
| Peripheral | `stm32-adc-dac` | Sampling time, calibration, reference, DMA, DAC waveforms |
| Peripheral | `stm32-timers-pwm` | Prescaler and reload, PWM, dead time, capture, encoder |
| Peripheral | `stm32-dma` | Request mapping, modes, memory reach, cache coherency |
| Peripheral | `stm32-qspi-fmc` | Quad/Octo-SPI flash, memory-mapped mode, FMC SRAM and SDRAM |
| RTOS | `stm32-freertos` | FreeRTOSConfig, interrupt priorities, HAL timebase, patterns, tickless idle |
| RTOS | `stm32-zephyr` | West workflow, devicetree overlays, Kconfig, drivers, MCUboot |

Invoke a skill as `/stm32:<skill-name>` (for example `/stm32:stm32-debug`), or describe the problem and Claude loads the matching skill from its description.

## Structure

Each skill is a folder with a short `SKILL.md` and a `references/` folder whose files Claude loads only when needed. `stm32-debug`, for example, has references for fault-register decoding, common causes by symptom, and a family map.

## Accuracy

Core-level facts (Arm architecture) are stated plainly. Family-level facts (register names, bit positions, errata, option-byte encodings, mode names) vary by part and silicon revision, so the skills tell Claude to flag them for verification against the reference manual, datasheet, and errata sheet. Treat generated code and numbers as drafts to verify on hardware.

## Connectors

Optional. See `CONNECTORS.md`. Skills use `~~source control`, `~~project tracker`, and `~~knowledge base` placeholders and work without any connector.

## License

MIT. See `LICENSE`.
