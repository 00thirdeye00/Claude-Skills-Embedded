# CAN and CAN FD

## Basics
- Two-wire differential bus (CANH, CANL) with a transceiver between the MCU and the bus. Each end of the bus has a 120 ohm terminator; with power off, about 60 ohm is measured between CANH and CANL.
- Messages carry an identifier (11-bit standard or 29-bit extended), a data length, up to 8 data bytes (classic CAN) or up to 64 (CAN FD), and a CRC. The identifier sets priority: arbitration is bitwise, and a dominant 0 wins, so the lower identifier has higher priority.
- Bit stuffing inserts a bit after five identical bits; the hardware handles it.
- Classic CAN reaches 1 Mbit/s on short buses; longer buses need lower rates. CAN FD can switch to a faster data-phase rate (bit rate switching) after arbitration; the achievable rate depends on the transceiver and topology.

## Bit timing
Each bit is divided into time quanta (Tq): 1 sync quantum, then segment 1 (propagation plus phase 1), then segment 2 (phase 2).

```
bit rate = f_can_clk / (prescaler * (1 + BS1 + BS2))
sample point = (1 + BS1) / (1 + BS1 + BS2)
```

Typical sample points are 75 to 87.5 percent. All nodes on a bus must use the same bit rate and compatible sample points. SJW (resynchronization jump width) lets nodes tolerate oscillator drift. In CAN FD, the nominal phase and the data phase have separate timing, and a transmitter delay compensation setting is needed at higher data rates.

## Errors
- Each node has transmit and receive error counters. Nodes move from error-active to error-passive, and to bus-off when the transmit counter exceeds 255. A bus-off node stops transmitting and must follow a recovery procedure.
- A node alone on a bus (no acknowledging receiver) sees acknowledge errors and drives its counter up.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| Error frames, bus-off | Bit rate mismatch, missing terminator, wrong clock | Measure bit time; check 60 ohm; confirm clock frequency |
| Nothing received | Receive filters not configured or too strict, transceiver in standby | Open the filter to accept all, check the transceiver control pins |
| Works on bench, fails in vehicle | Ground offset, EMI, stub length, sample point | Shorten stubs, check common-mode range, adjust sample point |
| Lost messages under load | Receive FIFO overrun, interrupt latency | Use deeper FIFOs, service in a high-priority task |
| CAN FD data corrupted | Data-phase rate too high for the transceiver or topology | Lower the data rate, enable delay compensation |
