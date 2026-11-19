---
name: stm32-bootloader-ota
description: Design, implement, and debug STM32 bootloaders and firmware updates: flash layout, jumping from a bootloader to an application, the built-in system bootloader and DFU, image validation with CRC or signatures, A/B slots and rollback, and MCUboot integration with or without Zephyr. Use when planning a bootloader or OTA update, an application does not start after a bootloader jump, flash writes fail, or an update must survive power loss. Trigger with "STM32 bootloader", "jump to application", "OTA update", "MCUboot on STM32", "system memory bootloader", "DFU mode", "app crashes after bootloader jump", "VTOR offset".
argument-hint: "<update source (UART/USB/OTA), flash size and layout, security needs, or the failure>"
---

# /stm32:stm32-bootloader-ota

Plan and implement a safe boot and update path on STM32.

## Usage

```
/stm32:stm32-bootloader-ota $ARGUMENTS
```

If details are missing, ask for the part number and flash organization, the update transport, whether images must be authenticated, whether rollback is required, and the RTOS.

## How It Works

```
┌───────────────────────────────────────────────────────────┐
│ 1 NEEDS    transport, security, rollback, flash budget     │
│ 2 LAYOUT   bootloader, slots, config, alignment            │
│ 3 BOOT     validate image, hand over cleanly               │
│ 4 UPDATE   receive, write, verify, activate, confirm       │
│ 5 TEST     power loss at every step, bad images, rollback  │
└───────────────────────────────────────────────────────────┘
```

## Steps

1. **Define needs**: how images arrive, whether they must be signed, whether a failed update must roll back, and how much flash can be spent.
2. **Choose an approach** with `references/bootloader-and-update.md`: the built-in system bootloader for simple programming, a custom bootloader, or MCUboot for signed images with swap and rollback.
3. **Design the flash layout** aligned to the erase granularity of the part. Note that some families have non-uniform sectors and some have two banks.
4. **Write the handover**: validate the image, deinitialize peripherals and interrupts, set the vector table and stack pointer, jump. Link the application for its slot address.
5. **Write the update logic**: receive in a staging area, verify, then activate; make the commit step atomic.
6. **Design tests**: power removed at every stage, truncated and corrupted images, wrong image for the device, downgrade attempts, and interrupted rollback.

## Output

```markdown
## Boot and Update Design: [product]

### Approach
[system bootloader / custom / MCUboot, with rationale]

### Flash layout
| Region | Start | Size | Purpose |
|---|---|---|---|

### Boot sequence
[steps]

### Update sequence
[steps, with the atomic commit point]

### Failure handling
| Failure | Behavior |
|---|---|

### Tests
- [test, expected result]
```

## Rules

- Take addresses, sector sizes, and entry methods from the reference manual and the application note for the system bootloader on the exact part.
- Design so that power loss at any point leaves a bootable device.
- Never enable irreversible protection settings as part of this workflow without explicit user confirmation.
- State flash timing and stall behavior assumptions, and where code must run from RAM.

## If Connectors Available

If **~~source control** is connected:
- Check the linker scripts and build configuration for slot offsets.

If **~~knowledge base** is connected:
- Look up the part's boot-mode application note and flash programming chapter.

## Tips

1. **After a jump, most failures are the vector table**: check `VTOR`, the application's link address, and the stack pointer value.
2. **Deinitialize what the bootloader used** (tick, interrupts, clocks) before the jump.
3. **Test the update path from the oldest shipped version.**
