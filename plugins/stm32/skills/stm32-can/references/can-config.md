# STM32 CAN and FDCAN configuration

HAL names are shown for orientation; confirm against your HAL version. Controller features and limits depend on the part.

## Contents
- Controller types
- Bit timing
- Filters
- Operation and interrupts
- Error handling
- CAN FD
- Failure modes

## Controller types

- **bxCAN**: classic CAN 2.0 controller, three transmit mailboxes, two receive FIFOs with three messages each, filter banks shared between controllers on dual-CAN devices. The second controller's filter banks start at a configurable index.
- **FDCAN**: supports classic CAN and CAN FD, with a message RAM holding filters, FIFOs, and transmit buffers. The kernel clock is selected in the clock tree, and the message RAM layout has to be configured.

## Bit timing

```
bit rate = kernel_clock / (prescaler * (1 + BS1 + BS2))
sample point = (1 + BS1) / (1 + BS1 + BS2)
```

Example: bxCAN on a 42 MHz bus clock for 500 kbit/s. Choose prescaler 6, giving a 7 MHz time-quantum clock, so 14 quanta per bit: `1 + BS1 + BS2 = 14`. With BS1 = 11 and BS2 = 2 the sample point is 12/14, about 85.7 percent. Use a synchronization jump width of 1 or 2. This example assumes the stated clock; recompute for your clock and compare against the network's required sample point.

Allow the tolerance of the oscillators in the network: a crystal on every node is usually required for higher rates.

## Filters

- On bxCAN, nothing passes until a filter is configured. A filter bank in mask mode with ID and mask both zero accepts everything.
- Use mask filters for ranges and list filters for exact IDs; assign messages to FIFO 0 or FIFO 1 to spread load.
- On FDCAN, configure the global filter for non-matching frames and set up standard and extended filter elements.

```c
CAN_FilterTypeDef f = {0};
f.FilterBank = 0;
f.FilterMode = CAN_FILTERMODE_IDMASK;
f.FilterScale = CAN_FILTERSCALE_32BIT;
f.FilterIdHigh = 0; f.FilterIdLow = 0;
f.FilterMaskIdHigh = 0; f.FilterMaskIdLow = 0;      /* accept all (for bring-up) */
f.FilterFIFOAssignment = CAN_RX_FIFO0;
f.FilterActivation = ENABLE;
HAL_CAN_ConfigFilter(&hcan1, &f);
```

## Operation and interrupts

Typical flow: initialize with the timing and mode, configure filters, start the controller, activate notifications (for example "FIFO 0 message pending"), receive in the callback by reading the message, and send by adding a message to a transmit mailbox and keeping the mailbox identifier for completion events. Drain the receive FIFO in a task for high rates, and track overruns.

Use loopback mode for a first test with no bus, silent mode to listen without driving the bus, and silent loopback for self-tests.

## Error handling

- Monitor the error counters and the last error code; log bus-off events.
- Enable automatic bus-off recovery or implement a recovery procedure with a delay, and limit retries so a faulty node does not flood the bus.
- A node alone on a bus will not receive acknowledgments and will rack up errors; this is expected.

## CAN FD

Select the frame format with bit-rate switching for a faster data phase. Configure separate nominal and data timing. At higher data rates enable transmitter delay compensation, and verify the transceiver supports the rate. Payloads up to 64 bytes need matching message RAM element sizes.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| Nothing received | Filters not set, wrong bit timing, transceiver standby or wiring | Open filters, measure bit time, check transceiver pins |
| Bus-off | Rate mismatch, no termination, no acknowledgment | Check rate, 60 ohm between the lines, another node present |
| Transmit stuck | No acknowledgment, mailbox not freed, bus error | Check the error counters and mailbox state |
| Lost frames | FIFO overrun | Increase servicing priority, use both FIFOs, filter earlier |
| FD data corrupted | Data-phase rate too high, timing or delay compensation wrong | Lower the data rate, adjust timing |
| Works on bench only | Ground offset, stubs, EMC | Check the wiring topology and the common-mode range |
