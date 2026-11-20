# Planning clocks, pins, DMA, memory, and interrupts

Confirm every number and register-level detail in the datasheet, reference manual, and errata sheet for the exact part.

## Contents
- Clock plan
- Pin plan
- DMA plan
- Memory plan
- Interrupt priority plan
- Timing and power budgets

## Clock plan

1. **Pick sources.** An external crystal (HSE) gives accuracy for USB, CAN, and precise baud rates. Internal oscillators (HSI, MSI) save cost and pins but are less accurate and drift with temperature, so check the datasheet accuracy against what each peripheral tolerates. Some families have a 48 MHz internal oscillator with clock recovery for USB.
2. **Set the PLL.** Respect the input, VCO, and output frequency limits. Write the divider and multiplier values and the resulting frequencies.
3. **Set bus prescalers.** Respect each bus's maximum frequency. Note that timer clocks are commonly doubled when the APB prescaler is not 1; confirm for the family.
4. **Check kernel clock selection.** Many families select peripheral kernel clocks (UART, I2C, SPI, ADC, USB, FDCAN) with muxes in RCC. List them with the chosen source and frequency.
5. **Set flash latency and voltage scaling** for the target frequency; apply flash latency before raising the clock.
6. **Plan low-power clocks**: which clocks run in stop modes, and what restarts after wake-up.

## Pin plan

1. Reserve: debug (SWDIO and SWCLK), reset, boot pin(s), oscillator pins, supply and reference pins, and any pins that carry boot-mode information at reset.
2. For each function, choose the pin from the datasheet alternate-function table. Record the AF number.
3. Check conflicts: one pin per function at a time, and one pin may serve several candidate functions.
4. Check electrical limits: 5 V tolerance of the pin type, per-pin and total current, and slew-rate setting for EMI.
5. Group related signals (for example a bus and its chip selects) on the same port where layout allows.
6. Keep spare pins for test points and future signals.
7. Treat the generated configuration project (for example a CubeMX project file) as the single source of truth if you use one, and keep it in version control.

## DMA plan

1. List transfers: peripheral, direction, data width, rate, circular or one-shot.
2. Map each to a DMA controller and stream or channel using the request mapping table (or the request multiplexer settings on families that have one).
3. Resolve conflicts: two requests on one stream cannot run at once; move one to another stream, controller, or use interrupts instead.
4. Check memory reach: some RAM regions cannot be accessed by DMA on some families.
5. Set priorities and decide between circular, double-buffer, and one-shot modes.

## Memory plan

| Region | Typical use |
|---|---|
| Flash start | Bootloader (if any) |
| Flash application slot | Application image, vector table at the slot start |
| Flash second slot or staging | Update image |
| Flash end | Configuration, calibration, counters (erase-sector aligned) |
| Main RAM | Stack, heap, .data, .bss |
| DMA-reachable RAM | DMA buffers |
| Special RAM (CCM, TCM, backup SRAM) | Fast data, retention; check bus-master access |

Align regions to erase granularity. Size stacks from analysis and measurement. Decide heap policy (static allocation preferred). On cached cores, put DMA buffers in a non-cacheable region or manage the cache.

## Interrupt priority plan

1. Use a single priority grouping for the whole project (RTOS ports commonly need all bits as preemption priority).
2. Assign levels by urgency: fault-critical and hard real-time handlers highest; everything that calls RTOS APIs at or below the RTOS maximum syscall priority.
3. Document the table in the design and keep it next to the code that sets it.
4. Check that no two handlers that must preempt each other share a level.

## Timing and power budgets

- **CPU load** = sum of (execution time / period) for each activity, with measured or conservatively estimated times, including ISR time.
- **Latency**: worst-case interrupt-to-response including interrupts-masked time.
- **Current**: sum of mode currents weighted by the time in each mode; add peripheral and external component currents.
- Record each as an estimate with a plan to measure.
