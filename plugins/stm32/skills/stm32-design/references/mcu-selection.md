# Selecting an STM32 part

All family descriptions are general guidance. Confirm every figure in the current datasheet and product selector for the exact part.

## Contents
- Selection steps
- Family positioning
- Questions that change the choice

## Selection steps

1. **Peripheral count and type.** Count instances (UART, SPI, I2C, CAN, USB, ADC channels, timers with the needed channels and features). Check that they are available on the same part and that the package exposes the pins.
2. **Throughput and CPU.** Estimate CPU load. Check for an FPU, DSP instructions, and special accelerators if the algorithm needs them. Prefer a margin of 30 to 50 percent.
3. **Memory.** Estimate flash (code, constants, bootloader slots, update slot) and RAM (stack, heap, buffers, DMA regions). Check the RAM layout, because not all RAM is reachable by all bus masters.
4. **Power.** Compare run, sleep, and stop currents, wake-up time, and the availability of low-power peripherals (low-power UART, timers, ADC).
5. **Package and board.** Pin count, package type, and layer count. Check pin compatibility between family members if you want a migration path.
6. **Features.** Security (secure boot, TrustZone, crypto), external memory interfaces, USB speed, CAN FD, Ethernet, display interfaces, wireless.
7. **Supply and environment.** Voltage range, temperature grade, and ESD or EMC needs.
8. **Ecosystem and supply.** HAL and RTOS support, Zephyr board support, toolchain, longevity, and availability.

## Family positioning

| Family | General positioning |
|---|---|
| C0, F0, G0 | Entry-level Cortex-M0 or M0+ cost-sensitive control |
| F1, F3 | Earlier mainstream and mixed-signal generations (check status for new designs) |
| G4 | Mixed-signal and motor-control oriented Cortex-M4 with fast analog and math accelerators |
| F4 | Mainstream performance Cortex-M4 with FPU, widely documented |
| L0, L4, L5, U5 | Ultra-low-power families; L5 and U5 add Cortex-M33 and TrustZone |
| F7, H7 | High-performance Cortex-M7 with caches and large memories |
| H5 | Cortex-M33 performance with security features |
| WB, WL, WBA | Wireless: BLE or 802.15.4 (WB, WBA), LoRa (WL) |

## Questions that change the choice

- Is USB or CAN required? That forces clock accuracy (crystal or a clock-recovery oscillator) and package pin choices.
- Is the product battery powered? Then low-power modes and wake-up time dominate the choice.
- Will you use an RTOS with many tasks? Budget RAM for stacks and kernel objects.
- Is there a bootloader and over-the-air update? Budget two image slots plus the bootloader, and check flash erase granularity.
- Is long-term supply required? Check the manufacturer's longevity program for the part.
