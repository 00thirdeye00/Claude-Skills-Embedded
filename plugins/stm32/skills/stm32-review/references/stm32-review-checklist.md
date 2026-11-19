# STM32 review checklist

Verify family-specific items against the reference manual, datasheet, and errata sheet for the exact part.

## Contents
- Clocks and power
- GPIO and pin multiplexing
- Interrupts and priorities
- DMA and cache
- HAL and LL usage
- RTOS integration
- Flash, option bytes, and boot
- Peripheral-specific
- Generic items summary

## Clocks and power
- Peripheral clock enabled before register access; reset state considered.
- Kernel clock source selected where the family uses muxes; frequency and baud or timing computed from the real source.
- `HSE_VALUE` and other clock constants match the hardware.
- Flash latency raised before increasing the system clock; voltage scaling matches the frequency.
- Oscillator and PLL start-up waits have timeouts and a failure path.
- Low-power entry and exit: wake sources, clock restore, peripheral state, debug settings.

## GPIO and pin multiplexing
- Alternate function numbers match the datasheet table; mode, speed, pull, and output type are correct for the signal.
- SWD pins and boot pins are not repurposed by accident.
- Unused pins are in a defined state; analog mode for lowest leakage where appropriate.
- Pin interrupt lines: one port per line number; shared interrupt vectors handled for each line.

## Interrupts and priorities
- Handler names match the startup file; C++ code uses C linkage.
- Interrupts are enabled in the NVIC and at the peripheral, and flags are cleared.
- A single priority grouping is set once; priority values use the correct scale (HAL functions take unshifted values, RTOS config macros often use shifted values).
- Handlers that call RTOS APIs are at or below the RTOS maximum syscall priority.
- SysTick priority is considered where HAL timeouts or `HAL_Delay` are used inside other interrupts.

## DMA and cache
- Request mapping is right for the chosen stream, channel, or multiplexer request.
- Data widths and alignment match between peripheral and memory.
- Buffers live in DMA-reachable RAM and outlive the transfer.
- On cached cores: cache clean before DMA reads, invalidate before CPU reads, buffers aligned and sized to the cache line, or a non-cacheable region.
- Transfer-complete, half-transfer, and error callbacks are enabled and handled; flags are cleared before restart.

## HAL and LL usage
- Return values are checked; HAL states are handled after errors.
- Handles are not stack variables when used with interrupt or DMA operations.
- Callback function names match the weak definitions.
- Blocking HAL calls with timeouts are not used inside interrupts or high-priority tasks.
- Generated code edits are inside the user-code markers so regeneration keeps them.
- LL and HAL are not mixed on the same peripheral without care for HAL state.

## RTOS integration
- Correct port for the core; kernel interrupt priorities set to the RTOS rules.
- HAL timebase uses a timer separate from the RTOS tick.
- Stack sizes use the correct units and have measured margin; overflow detection is enabled.
- Only ISR-safe APIs are called from interrupts; tasks do not busy-wait.
- Mutexes protect shared peripherals (one bus, several tasks).

## Flash, option bytes, and boot
- Linker script flash and RAM regions match the part; vector table address matches the image location.
- Flash programming code handles erase granularity, alignment, program size, and stalls while the flash is busy.
- Option bytes (read protection, write protection, watchdog mode, boot configuration) are set deliberately and documented.
- Application started by a bootloader sets the vector table offset and has interrupts in a clean state.
- Watchdog is configured for the release build and fed from a health-checked place.

## Peripheral-specific
- UART: baud error acceptable; overrun and framing errors handled; frame detection method chosen.
- I2C: address format (7-bit shifted) correct; timeouts and bus recovery present.
- SPI: mode, bit order, frame size, and chip-select timing match the device; chip select released after the busy flag clears.
- CAN: bit timing computed from the real kernel clock; receive filters configured; error and bus-off handling present.
- USB: 48 MHz clock accurate; interrupts serviced promptly; descriptors valid; low-power behavior defined.
- ADC: calibration, sample time versus source impedance, reference voltage, and trigger configuration.
- Timers: prescaler and reload computed with the real timer clock; preload settings; output enable for advanced timers.

## Generic items summary
Concurrency (shared data protection), memory safety (bounds, stack), error handling (every wait has a timeout), security (input validation, debug policy), and tooling (strict warnings, static analysis). Use `/embedded-core:embedded-review` from the `embedded-core` plugin for the full list.
