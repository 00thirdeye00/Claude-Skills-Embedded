# STM32 Ethernet (MAC, PHY, LwIP)

Availability, MII/RMII options, and descriptor handling differ by family. Confirm in the reference manual and the PHY datasheet.

## Setup checklist
- **Interface**: RMII (fewer pins, needs a 50 MHz reference clock) or MII. Decide who sources the RMII clock: the PHY, an external oscillator, or an MCU clock output; the choice affects the clock tree and pin plan.
- **Pins**: assign the Ethernet alternate functions from the datasheet; keep RMII traces short and matched; add the PHY's strap resistors as its datasheet requires.
- **PHY**: reset timing (hold reset, then wait before the first management access), management bus address from the strap pins, auto-negotiation enabled, link and speed read back from the PHY status register.
- **MAC address**: use an address you are entitled to use; do not hard-code a shared one across units.
- **Descriptors and buffers**: place them in RAM the Ethernet DMA can reach. On cached cores, put them in a non-cacheable region or manage the cache around every transfer.
- **Checksum offload and filtering**: enable hardware checksum offload only if the stack is configured for it; configure the multicast and broadcast filters you need.

## LwIP integration
- Choose the OS-aware mode with an RTOS (a dedicated input task fed by an interrupt semaphore) or the no-OS mode with polling in the main loop.
- Size the heap, the packet buffer pool, TCP window, and the number of connections from measured traffic; running out shows up as stalls, not errors.
- Give the TCP/IP task and the input task enough stack and an appropriate priority; do not call the stack from interrupts.
- Report link-up and link-down to the stack so it restarts DHCP and ARP.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| No link | PHY not reset or wrong address, cabling, clock | PHY ID register read, link LED, RMII clock present |
| Link up, no traffic | Reference clock wrong, MAC/PHY speed or duplex mismatch, filters | Scope the 50 MHz clock, read negotiated speed and duplex |
| Works for a while, then stalls | Receive buffers exhausted, descriptors not returned, heap or pool too small | Statistics counters, pool usage |
| Corrupted frames | Descriptors in the wrong RAM, cache coherency, checksum settings | Descriptor placement, cache maintenance |
| High latency | Priorities, input task starved, interrupt too low | Task priorities and interrupt priority |
