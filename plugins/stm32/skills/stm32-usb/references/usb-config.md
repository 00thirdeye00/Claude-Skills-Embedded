# STM32 USB configuration

Peripheral types, clock options, and middleware differ by family. Confirm in the reference manual and the datasheet for the part.

## Contents
- Peripheral types
- Clock
- Hardware checklist
- Stack and class options
- CDC notes
- Low power and DFU
- Failure modes

## Peripheral types

- **Full-speed device peripheral** (found on many small and mid-range parts): dedicated packet memory, fixed endpoint count.
- **OTG full-speed**: device, host, or dual-role with a FIFO-based memory.
- **OTG high-speed**: needs an external ULPI PHY on many parts, or has an internal full-speed PHY used in full-speed mode.
- USB-C power delivery is a separate peripheral on parts that have it.

## Clock

Full-speed operation requires a 48 MHz clock with tight tolerance. Sources: the main PLL's dedicated output, a crystal-less 48 MHz internal oscillator plus clock recovery on parts that have it, or a crystal-based PLL. Check that the PLL output divider produces exactly 48 MHz with your system clock settings; choosing a system clock that cannot also yield 48 MHz is a common design trap. Select the clock source for the USB kernel clock mux where present.

## Hardware checklist

- D+ (full-speed) pull-up: internal software-controlled, internal fixed, or external with a switch; follow the datasheet for the part and the board.
- VBUS: for bus-powered or self-powered designs, decide on VBUS sensing, and configure the peripheral to match the wiring; a wrong setting makes the device ignore the bus.
- Series resistors and ESD protection as recommended by the datasheet.
- Crystal accuracy if no clock recovery is used.
- Pin configuration for the USB data pins, with the alternate function set where the family requires it.

## Stack and class options

Options include the vendor's USB device middleware, open-source stacks (such as TinyUSB), and the Zephyr USB stack. Common classes: CDC (serial), HID, mass storage, DFU, and composite devices.

Descriptors define the device. Use correct lengths, endpoint addresses and sizes, and string indices. Use your own vendor and product IDs. Test on several host operating systems.

Interrupt priority: choose it consistent with RTOS rules if the stack calls RTOS APIs, and make sure the USB interrupt can preempt long non-critical work. Size the stack, heap, and buffers according to the middleware's requirements; some middleware allocates dynamically.

## CDC notes

- The transmit function returns busy if the previous packet has not completed; handle it with a queue and a retry, with a timeout when the host is not reading.
- Detect the host's connection (line-state control request) before sending, otherwise data may be dropped or the transmit may block.
- Large transfers should be split into packets of the endpoint size, with a zero-length packet when a transfer ends on a packet boundary.
- Receive data in the callback by copying into a ring buffer and re-arming the receive.

## Low power and DFU

- Handle suspend and resume: reduce current on suspend and restore clocks and peripherals on resume. Check how the clock for USB behaves in the chosen low-power mode.
- Entering the built-in system bootloader in DFU mode from the application means deinitializing USB and jumping to system memory; see the bootloader skill. Check the part's boot application note for the supported DFU interface.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| No device on the host | Clock not 48 MHz, D+ pull-up inactive, VBUS setting wrong, pins | Measure the clock; scope D+; review pull-up and VBUS configuration |
| Enumeration fails midway | Descriptor error, control-transfer bug, interrupt starvation | Host USB log or analyzer; validate descriptors; check the interrupt priority |
| Disconnects after a few seconds | Watchdog, brown-out, clock drift, suspend mishandling | Check power rails, clock, and suspend path |
| CDC stalls | Host not reading, busy handling absent, buffer too small | Add timeout and queue; check line-state handling |
| Works on one OS only | Class-specific descriptor details | Compare with a known-good descriptor set |
| Fails in low-power modes | USB clock stopped | Verify the clock source is kept or restarted |
