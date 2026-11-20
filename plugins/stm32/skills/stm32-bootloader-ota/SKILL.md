---
name: stm32-bootloader-ota
description: Design and debug an STM32 boot and update path: flash layout, bootloader handover, DFU, A/B slots with rollback, and MCUboot.
argument-hint: "<update source (UART/USB/OTA), flash size and layout, security needs, or the failure>"
disable-model-invocation: true
---

# /stm32:stm32-bootloader-ota

Plan and implement a safe boot and update path on STM32.

If details are missing, ask for the part number and flash organization, the update transport, whether images must be authenticated, whether rollback is required, and the RTOS.

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

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
