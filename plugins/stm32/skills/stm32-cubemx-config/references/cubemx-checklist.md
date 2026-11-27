# CubeMX settings checklist

Names follow common CubeMX layouts; confirm them in your version.

## Contents
- Order of work
- Pinout and configuration
- Clock configuration
- System core and NVIC
- Middleware
- Project manager
- After generation
- Reviewing an .ioc

## Order of work

1. Select the exact part. 2. Pins and peripherals. 3. Clocks. 4. System core (debug, timebase). 5. DMA and NVIC. 6. Middleware. 7. Project settings. 8. Generate. Check each against the design before moving on.

## Pinout and configuration

- Assign pins to the design's alternate functions; confirm no pin carries two functions and that debug pins are kept as intended.
- Enable each peripheral in the mode the design says (for example I2C, SPI full duplex master, UART asynchronous, FDCAN, USB device class).
- Set peripheral parameters from the design: baud rate or timing, data width, FIFO or DMA settings, error handling options.
- GPIO: set output level at start, pull, speed, and user labels for named signals.

## Clock configuration

- Select the oscillator source and frequency to match the board (crystal, bypass, internal), and the PLL source.
- Enter the target system clock and let the tool compute dividers; check each bus and peripheral clock against its maximum, and note kernel clock selections for UART, I2C, USB, ADC, FDCAN.
- Check flash latency and voltage scaling are consistent with the target frequency.

## System core and NVIC

- SYS: debug interface (for example serial wire), and timebase source. With an RTOS, move the HAL timebase to a spare timer, not the system tick.
- NVIC: set the priority grouping the design uses (all bits preemption for FreeRTOS), then assign each interrupt's priority from the design table; leave RTOS-calling interrupts at or below the kernel limit.
- Enable the interrupt for each peripheral that needs it; mark DMA interrupts.
- DMA: assign the request to the stream or channel in the design, direction, mode (normal or circular), data widths, increments, and priority.

## Middleware

- FreeRTOS (CMSIS-RTOS v2 or native): tick rate, maximum priorities, heap scheme and size, stack-overflow checking, static or dynamic allocation, and the tasks and queues from the design. Note stack-size units differ between wrappers.
- USB device: class, descriptors strings, VID and PID (use your own), buffer sizes.
- File systems and other stacks: memory and interrupt settings from the design.

## Project manager

- Toolchain or IDE target (CMake, IDE project, makefile).
- Code generator: generate a `.c` and `.h` pair per peripheral; keep user code on regeneration; copy only the necessary library files or reference them, per your repository policy.
- Minimum heap and stack sizes (linker script values) from the design.
- Firmware package version: record it, so the team uses the same one.

## After generation

- Write code only in the user-code sections, or in separate source files that call generated functions.
- Wrap generated handles behind the board support layer so upper layers do not include generated headers.
- Commit the `.ioc` and generated files; review diffs after each regeneration.
- Re-run the design checks: pins, clock values in the generated `SystemClock_Config`, priorities in generated code.

## Reviewing an .ioc

The `.ioc` is a text properties file. Search it for the pin signal assignments, the RCC and clock values, the NVIC priority entries, the DMA entries, and the timebase source. Compare each with the design table and list differences with the design item they contradict.
