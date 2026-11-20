# USB (device side)

## Basics
- Speeds: low 1.5 Mbit/s, full 12 Mbit/s, high 480 Mbit/s, plus SuperSpeed variants on larger devices. Most microcontrollers implement full-speed device, some also high-speed.
- The host enumerates the device: it resets the bus, reads the device descriptor, assigns an address, then reads the configuration, interface, endpoint, and string descriptors, and finally selects a configuration.
- Endpoint types: control (endpoint 0, setup and status), bulk (reliable, no latency guarantee), interrupt (bounded latency, small data), isochronous (fixed bandwidth, no retries).
- Common classes: CDC (virtual serial port), HID (keyboards, mice, custom reports), MSC (mass storage), DFU (firmware update).
- A full-speed device signals its presence with a pull-up resistor on D+ (low-speed on D-). Some MCUs control this pull-up in software, some need an external pull-up, and some require a GPIO to switch it.
- Full-speed operation needs a 48 MHz clock with tight tolerance (about 0.25 percent), usually from a PLL fed by a crystal, or from an on-chip 48 MHz oscillator with clock recovery that locks to the host's frames.
- Power: a bus-powered device may draw up to 100 mA before configuration and up to 500 mA after configuring for it in USB 2.0; suspended devices must draw very little.
- Vendor and product IDs identify the device. Use IDs you are entitled to use; open hardware projects can request IDs from an open registry.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| Host does not see a device | No D+ pull-up, wrong 48 MHz clock, cable or VBUS issue, pins not set up | Scope D+ and D-; check clock configuration; check pull-up control |
| Device found, enumeration fails | Descriptor errors, control-transfer handling, stack not serviced in time | Use a USB analyzer or the host's USB log; validate descriptors |
| Enumerates, then drops | Suspend handling, interrupt starvation, power issues, clock drift | Check the interrupt priority, watchdogs, and brown-outs |
| CDC loses or stalls data | Host not reading, transmit-busy handling, buffers too small | Check the busy flag before send, add timeouts and a TX queue |
| Works on one OS only | Descriptor quirks, missing class-specific descriptors or OS descriptors | Test on more hosts; compare with a reference descriptor set |
| Fails only in low-power modes | Clock stops, wake-up configuration | Verify the USB clock stays alive or is restarted on resume |

Service USB interrupts promptly and keep long operations (flash writes, blocking prints) out of the USB path.
