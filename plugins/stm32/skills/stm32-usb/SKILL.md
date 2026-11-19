---
name: stm32-usb
description: Configure and debug STM32 USB device and host: USB peripheral type (full-speed device, OTG full-speed, OTG high-speed), the 48 MHz clock, D+ pull-up and VBUS handling, CDC virtual COM port, HID, mass storage, DFU, descriptors, middleware choices, and low-power behavior. Use when a board does not enumerate, drops off the bus, loses CDC data, or when selecting a USB class or stack. Trigger with "STM32 USB", "USB CDC", "USB not enumerating", "device not recognized", "USB DFU", "USB HID", "USB clock 48 MHz", "VBUS sensing".
argument-hint: "<class, speed, host OS, clock source, or the symptom>"
---

# /stm32:stm32-usb

Configure STM32 USB and diagnose enumeration and data-transfer problems.

## Usage

```
/stm32:stm32-usb $ARGUMENTS
```

If details are missing, ask for the part, the USB instance and speed, the class (CDC, HID, MSC, DFU), the clock source, power topology, host OS, and what the host reports.

## Workflow

1. **Identify the USB peripheral** on the part and whether an external high-speed PHY is used.
2. **Plan the 48 MHz clock** and its accuracy; check crystal-less options and clock recovery where the part has them.
3. **Plan the hardware**: D+ pull-up control, VBUS detection or self-powered configuration, ESD protection, series resistors per the datasheet.
4. **Choose the stack and class**, set descriptors, and size buffers, stack, and heap.
5. **Bring up** until the host enumerates, then test data transfer, unplug and replug, and suspend and resume.

Details, configuration checklists, example code, and failure modes are in `references/usb-config.md`.

## Choosing an approach

| Need | Use |
|---|---|
| Virtual serial port | CDC class with a transmit queue and busy handling |
| Keyboard, mouse, custom reports | HID class with report descriptors |
| File access | Mass-storage class over flash, SD, or RAM disk, with host-write handling |
| Firmware update over USB | DFU class, or the built-in system bootloader if its DFU mode suffices |
| Highest bandwidth | High-speed USB with an on-chip or external PHY and suitable RAM |

## Output

```markdown
## USB Plan: [context]

### Hardware plan (clock, pull-up, VBUS, power)
- [..]

### Stack and descriptor plan
- [..]

### Bring-up and test steps
- [..]
```

## Rules

- Do not ship example vendor and product IDs from vendor demos; use IDs you are entitled to use.
- Take the clock accuracy requirement from the reference manual and the USB specification.
- Keep USB interrupt service short and at a priority consistent with the RTOS rules.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **Not enumerating** usually means clock, D+ pull-up, descriptors, or stack start order.
2. **Check the host log** (device manager or system log) for the enumeration step that failed.
3. **Test replug and sleep/wake**; many bugs appear only there.
