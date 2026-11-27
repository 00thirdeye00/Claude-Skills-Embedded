---
name: stm32-peripherals
description: Set up or troubleshoot one STM32 peripheral: GPIO/EXTI, UART, I2C, SPI, CAN, USB, ADC/DAC, timers, DMA, QSPI/FMC, Ethernet, SD card, audio, display, RTC, watchdogs, CRC/RNG, OPAMP/COMP.
argument-hint: "<peripheral, part, rates or modes, or the symptom>"
disable-model-invocation: true
---

# /stm32:stm32-peripherals

Configure or troubleshoot one STM32 peripheral at a time.

## Workflow

1. Identify the peripheral, the exact part, the software layer (HAL, LL, register-level, Zephyr), the rates and modes needed, and the symptom or capture. Ask only for what is missing.
2. Load the one matching reference, not all of them.
3. Compute from the real clocks and show the numbers (baud, prescaler, timing, bit timing).
4. Give the configuration, the transfer-mode choice, error handling, and a verification step with a scope or logic analyzer.
5. List items to confirm against the reference manual, datasheet, and errata sheet for the exact part.

## References

| Peripheral | Load |
|---|---|
| GPIO, EXTI | `references/gpio-exti.md` |
| UART, USART, LPUART, RS-485 | `references/uart-config.md` |
| I2C | `references/i2c-config.md` |
| SPI | `references/spi-config.md` |
| CAN, FDCAN | `references/can-config.md` |
| USB | `references/usb-config.md` |
| ADC, DAC | `references/adc-dac-config.md` |
| Timers, PWM | `references/timers-pwm-config.md` |
| DMA | `references/dma-config.md` |
| QSPI, OctoSPI, FMC | `references/qspi-fmc-config.md` |
| Ethernet, LwIP | `references/ethernet-config.md` |
| SD card (SDMMC), FatFS | `references/sdmmc-config.md` |
| I2S, SAI audio | `references/i2s-sai-config.md` |
| LTDC, DMA2D, displays | `references/ltdc-display-config.md` |
| RTC, backup domain | `references/rtc-backup-config.md` |
| IWDG, WWDG watchdogs | `references/watchdog-config.md` |
| CRC unit, RNG | `references/crc-rng-config.md` |
| OPAMP, comparators | `references/analog-opamp-comp-config.md` |

## Rules

- Take alternate-function numbers, DMA request mappings, and limits from the datasheet and reference manual, not from memory.
- Mark family-specific facts for verification on the exact part and silicon revision.
- For fault-register decoding use `/stm32:stm32-debug`; for bus theory and sizing use `embedded-protocols` from `embedded-core`.
