# Common STM32 failure causes, by symptom

Each item gives the check and the usual fix. Core-level behavior is stable; register names, bit positions, and errata vary by family, so confirm them in the reference manual, datasheet, and errata sheet for the exact part and silicon revision.

## Contents
- Peripheral silent
- Interrupts
- DMA
- Clock and flash
- HAL
- RTOS
- Debug versus standalone
- Bus-specific quick checks

## Peripheral silent

1. **Bus clock not enabled.** Enable the peripheral's RCC bit before touching its registers. After enabling, read the RCC register back (the HAL `__HAL_RCC_xxx_CLK_ENABLE()` macros do this) because some families need a short delay before the first access.
2. **Kernel clock not selected.** Newer families (L4, G0, G4, H7, U5 and others) route UART, I2C, SPI, ADC, and USB kernel clocks through selection muxes in RCC. A wrong source gives wrong baud rates and timing, or a dead peripheral. Check the mux and the source's frequency.
3. **Peripheral held in reset.** Check the RCC reset register bit.
4. **GPIO alternate function.** Take the AF number from the **datasheet** alternate-function table, not the reference manual. Set the pin mode to alternate function, then check speed, pull-up or pull-down, and open-drain where the bus needs it.
5. **Pin conflicts.** SWD pins (commonly PA13 and PA14) lose the debugger if reconfigured. On F1, JTAG pins and AFIO remap need explicit handling.
6. **Power domain.** Backup-domain peripherals (RTC, backup registers) need backup-domain write access enabled in the power controller. Parts with separate analog or USB supplies need those rails present and, on some families, enabled in software. High-end parts with internal regulators or SMPS need the supply configuration done before raising voltage scale.
7. **Init order.** Enable clocks and configure pins before calling the HAL init for the peripheral. HAL `MspInit` callbacks must actually run; a renamed or missing callback silently leaves the weak default.

## Interrupts

1. **Handler name must match the vector table.** Names come from the startup file (for example `USART2_IRQHandler`). A misspelled or C++-mangled handler never links in, and the weak default handler loops forever. Declare handlers `extern "C"` in C++.
2. **Enable in the NVIC** with `NVIC_EnableIRQ` (or the HAL equivalent) and enable the interrupt source in the peripheral.
3. **Clear the flag.** If the interrupt flag is never cleared, the ISR re-enters forever. Clear in the order the reference manual specifies, and keep ISRs short.
4. **Stuck in `Default_Handler`.** Read `SCB->ICSR` (`VECTACTIVE`) to see the active exception number. Subtract 16 for the IRQ number.
5. **Priority grouping.** Set one grouping consistently at startup. FreeRTOS on Cortex-M requires all priority bits as preemption priority (`NVIC_PRIORITYGROUP_4` in HAL).
6. **Vector table location.** After a bootloader jump, `SCB->VTOR` must point at the application's table, and the application must be linked at that address.

## DMA

1. **Request mapping.** Use the request-to-stream/channel table in the reference manual (or the DMAMUX request ID on newer families). A wrong mapping runs nothing and raises no error.
2. **Peripheral DMA enable.** The peripheral usually has its own DMA request bit (for example the DMA transmit/receive enable bits on a UART). Enable it.
3. **Memory not reachable by DMA.** Examples: CCM data RAM on STM32F4 cannot be accessed by DMA; on STM32H7 the DMA1/DMA2 controllers cannot reach DTCM or ITCM. Place DMA buffers in DMA-reachable RAM through the linker script.
4. **Cache coherency (F7, H7, and other cached cores).** The CPU data cache and DMA do not see the same data unless you manage it. Clean the cache range before DMA reads from memory (transmit), invalidate before the CPU reads DMA-written data (receive), align and size buffers to the cache line (32 bytes on Cortex-M7), or place buffers in a non-cacheable MPU region.
5. **Buffer lifetime.** The buffer must outlive the transfer. A buffer on the stack of a returning function corrupts data.
6. **Width, alignment, and FIFO.** Peripheral width, memory width, and burst settings must be consistent with the buffer alignment.
7. **Restarting.** Clear transfer-complete and error flags before restarting a transfer. In circular mode, check the half- and full-transfer callbacks are enabled.
8. **Memory-to-memory.** On the DMA1/DMA2 families that have both, memory-to-memory is available only on DMA2 on several series; check the reference manual.

## Clock and flash

1. **Flash wait states.** Raise the flash latency before increasing SYSCLK and lower it after decreasing. Too few wait states gives random faults and garbage execution at speed.
2. **PLL and oscillator startup.** Check lock flags with timeouts. A missing or wrong HSE crystal makes startup hang; compare `HSE_VALUE` in the HAL configuration with the real crystal, because a mismatch skews every derived clock and baud rate.
3. **Voltage scaling and overdrive.** High frequencies need the matching voltage scale (and overdrive on some F4/F7 parts) set before raising the clock.
4. **Clock security system.** A CSS event raises an NMI; handle it or it looks like a random reset.
5. **Prescaler limits.** Check each bus's maximum frequency in the datasheet, and remember timer clocks may double when the APB prescaler is not 1.

## HAL

1. **`HAL_Delay` and timeouts depend on SysTick.** If code running at a priority at least as urgent as SysTick (numerically equal or lower) calls a HAL function that waits on the tick, the tick never advances and the call hangs. Give SysTick a high priority (urgent) or avoid blocking HAL calls in ISRs.
2. **HAL tick with an RTOS.** FreeRTOS uses SysTick for the scheduler. Move the HAL tick to a spare timer (CubeMX offers this) to avoid conflicts.
3. **HAL state machine.** After an error, a handle can stay in `HAL_BUSY` or an error state. Abort or reinitialize the peripheral rather than retrying blindly.
4. **Handles and buffers must outlive the call** for interrupt and DMA modes. Static or global storage, not locals.
5. **Callbacks are weak functions.** A typo in the callback name means it is never called. Compare against the HAL header.

## RTOS

1. **Stack overflow.** In FreeRTOS enable `configCHECK_FOR_STACK_OVERFLOW = 2`, implement `vApplicationStackOverflowHook`, and watch `uxTaskGetStackHighWaterMark`. Remember units: native FreeRTOS `xTaskCreate` takes the stack depth in **words**, while the CMSIS-RTOS2 `osThreadAttr_t.stack_size` is in **bytes**.
2. **Interrupt priority versus the RTOS limit.** Only interrupts with a priority numerically greater than or equal to `configMAX_SYSCALL_INTERRUPT_PRIORITY` (that is, equally or less urgent) may call `...FromISR` functions. STM32 implements a limited number of priority bits (commonly 4), and `configMAX_SYSCALL_INTERRUPT_PRIORITY` is expressed shifted into the top bits, while `HAL_NVIC_SetPriority` takes the unshifted value. A mismatch triggers the `configASSERT` in the port layer.
3. **Wrong API in an ISR.** Use the `FromISR` variants and the yield-from-ISR pattern. Never block in an ISR.
4. **Wrong port.** Select the port that matches the core: Cortex-M0 or M0+, M3, M4F, M7, or M33 each have their own.
5. **Heap exhaustion.** `pvPortMalloc` returns NULL when the heap in `configTOTAL_HEAP_SIZE` is exhausted. Enable the malloc-failed hook and size the heap from measured usage.
6. **Locking.** Use mutexes (with priority inheritance) for shared resources, not binary semaphores, to avoid unbounded priority inversion.

## Debug versus standalone

1. **Debug freeze bits.** The debug configuration registers (for example `DBGMCU`) decide whether watchdogs and timers keep running while the core is halted, and whether the debug interface stays alive in Sleep, Stop, and Standby. A watchdog frozen under the debugger hides resets that appear standalone.
2. **Low-power debug.** Without the debug-in-low-power bits set, the debugger loses the target when the core sleeps.
3. **Semihosting.** `printf` over semihosting stalls forever without a debugger attached.
4. **Boot configuration.** A floating `BOOT0` pin, boot-related option bytes, or read-out protection changes how the part starts. With read-out protection enabled, the debugger cannot connect.
5. **Startup timing.** Supply ramp, crystal startup, and external devices can need more time standalone than under the debugger.
6. **Optimization and undefined behavior.** Fails only when optimized: missing `volatile` on ISR-shared variables or registers, uninitialized variables, data races, strict-aliasing violations.
7. **Stack and heap sizes.** Default linker-script stack and heap sizes are small. Compare against measured usage, and check that the heap and stack do not collide in the map file.
8. **Reset loops.** Check the reset flags in the RCC control and status register (watchdog, brown-out, software, pin) to identify the reset source before guessing.

## Bus-specific quick checks

Deeper treatment is in the matching `stm32-<peripheral>` skill. First-pass checks:

- **I2C:** HAL expects the 7-bit address shifted left by one. Confirm pull-up values for the bus speed. A stuck bus is often a slave holding SDA low: toggle SCL up to nine times, issue a stop, and reset the peripheral. On families with a timing register, generate the value with the vendor tool or the reference-manual formulas.
- **SPI:** CPOL and CPHA must match the slave; check NSS handling (hardware versus software NSS, master-mode fault if NSS is pulled low), baud divider against the slave's maximum clock, and frame size.
- **UART:** Check kernel clock source and baud error, overrun flag handling, and DMA idle-line handling for variable-length frames.
- **CAN:** Bit timing and sample point must match the bus. On bxCAN, nothing is received until a filter is configured. Check termination and use loopback or silent mode for bring-up.
- **USB:** Needs an accurate 48 MHz clock, correct pull-up and VBUS handling, and enough stack and heap for the class stack.
