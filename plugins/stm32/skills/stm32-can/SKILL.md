---
name: stm32-can
description: Configure and debug STM32 CAN (bxCAN) and FDCAN: bit timing from the kernel clock, receive filters, mailboxes and FIFOs, interrupts, error and bus-off handling, loopback and silent modes for bring-up, and CAN FD data-phase settings. Use when a CAN node sends no frames, receives nothing, goes bus-off, or when choosing timing and filters. Trigger with "STM32 CAN", "bxCAN filter", "FDCAN setup", "CAN bit timing", "CAN bus-off", "CAN receives nothing", "CAN FD bitrate switching".
argument-hint: "<bit rate, frame formats, filters, topology, or the symptom>"
---

# /stm32:stm32-can

Configure STM32 CAN controllers and diagnose bus problems.

## Usage

```
/stm32:stm32-can $ARGUMENTS
```

If details are missing, ask for the part and CAN instance, bit rates, ID scheme, whether CAN FD is needed, the transceiver and termination, and any error counters or captures.

## Workflow

1. **Identify the controller**: bxCAN (classic CAN) or FDCAN (classic and FD) on the exact part.
2. **Compute bit timing** from the kernel clock for the target rate and a sample point matching the network.
3. **Configure receive filters** (nothing is received on bxCAN until a filter is set), FIFOs, and interrupts.
4. **Bring up** in loopback or silent mode, then on the bus with a second node or analyzer.
5. **Add error handling**: error counters, bus-off recovery, and overrun handling.

Details, configuration checklists, example code, and failure modes are in `references/can-config.md`.

## Choosing an approach

| Situation | Use |
|---|---|
| First bring-up without a bus | Loopback mode |
| Observe a bus without disturbing it | Silent mode |
| Accept a range of IDs | Mask or range filters, one bank per rule |
| High message rates | Interrupt on FIFO pending, drain the FIFO in a high-priority task |
| CAN FD with faster data phase | Separate data-phase timing and transmitter delay compensation |

## Output

```markdown
## CAN and CAN FD Plan: [context]

### Bit timing calculation
- [..]

### Filter plan
- [..]

### Interrupt and handling plan
- [..]

### Error and recovery plan
- [..]
```

## Rules

- Compute timing from the real kernel clock and show the sample point.
- Never leave the node on a bus with a wrong bit rate; test in silent or loopback mode first.
- Check transceiver pins and termination before debugging firmware.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **No frames received** is nearly always filters or bit timing.
2. **Bus-off** after the first transmit often means no other node acknowledges or the rate is wrong.
3. **Use an analyzer** to compare the sample point and bit time.
