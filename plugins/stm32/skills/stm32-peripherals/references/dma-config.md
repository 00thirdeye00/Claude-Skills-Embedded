# STM32 DMA configuration

DMA architecture differs significantly by family. Confirm all mappings and capabilities in the reference manual for the exact part.

## Contents
- Architectures
- Mapping requests
- Modes
- Widths, FIFO, burst
- Memory reach and cache
- Interrupts and flags
- HAL pattern
- Failure modes
- Quick selection guide
- Tips

## Architectures

- **Stream and channel controllers** (for example on F2, F4, F7): several streams per controller, each with a selectable channel from a fixed table; FIFO and burst options; memory-to-memory only on some controllers.
- **Channel controllers with a request multiplexer** (for example on G0, G4, L4, H7 and others): any request can be routed to any channel through a multiplexer; check the request ID tables.
- **High-performance families** add more controllers for different bus domains and memories (for example a master DMA for large transfers and a basic DMA for the low-power domain); each controller can reach different RAMs.

## Mapping requests

Each peripheral request has a fixed position in the mapping table of the reference manual (stream and channel, or request ID). Two requests that map to the same stream cannot run concurrently. Resolve conflicts by moving to another controller, or by using interrupts for the lower-rate peripheral. Enable the peripheral's own DMA request bit as well.

## Modes

| Mode | Behavior | Use |
|---|---|---|
| Normal | Transfers the count once and stops | Single blocks |
| Circular | Reloads automatically and wraps | Continuous sampling, serial receive |
| Double buffer | Alternates between two memory addresses | Gapless streaming with a callback per half |
| Memory to memory | Copies without a peripheral | Block moves on controllers that support it |

Half-transfer and transfer-complete interrupts let the CPU work on one half while the DMA fills the other. Counters decrement as items transfer, and the remaining count shows the position in circular mode.

## Widths, FIFO, burst

- Peripheral and memory data widths (byte, half-word, word) must match the data format and buffer alignment. A half-word peripheral register with byte memory width needs packing options understood.
- Address increment applies to memory, normally not to the peripheral data register.
- FIFO and burst settings, where available, improve bus efficiency but impose alignment and size constraints; in direct mode, they are off.
- Priority levels arbitrate between channels on one controller.

## Memory reach and cache

- Some RAM regions cannot be reached by DMA: examples include core-coupled RAM on some F4 parts and tightly coupled memories on F7 and H7 parts for some controllers. Place DMA buffers in reachable RAM with linker script sections.
- On cores with data caches, DMA writes to memory are not seen by the cache and CPU writes may sit in the cache. Before a DMA read of memory, clean the cache lines; after a DMA write, invalidate them before the CPU reads. Align buffers and sizes to the cache line (32 bytes on Cortex-M7), or place them in a non-cacheable region configured through the MPU.
- Keep buffers valid for the whole transfer; do not use locals.

## Interrupts and flags

Flags include half transfer, transfer complete, transfer error, and on some controllers FIFO error and direct-mode error. Clear the flags before starting a new transfer. Transfer errors usually indicate a bad address, an unreachable region, or a width and alignment violation. Keep DMA handlers short and process data in a task.

## HAL pattern

```c
/* Link a DMA handle to the peripheral handle (generated code does this). */
__HAL_LINKDMA(&huart2, hdmarx, hdma_usart2_rx);

HAL_UART_Receive_DMA(&huart2, rx_buf, RX_BUF_LEN);     /* start; circular if configured */

void HAL_UART_RxHalfCpltCallback(UART_HandleTypeDef *h) { /* first half valid */ }
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *h)     { /* second half valid */ }
```

Callback names depend on the peripheral and the HAL version. Check the DMA handle state before restarting and handle error callbacks.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| No transfer happens | Wrong request mapping, peripheral request bit off, channel disabled, clock off | Re-read the mapping table; check the enable bits and the DMA clock |
| Stops after one transfer | Normal mode where circular was wanted, or flags not cleared | Check the mode and the flags |
| Wrong data on cached cores | Cache not cleaned or invalidated, buffer not aligned | Apply cache maintenance, align buffers |
| Transfer error flag | Bad address, unreachable RAM, width or alignment violation | Check the buffer location and settings |
| Corrupt data after a long run | Overrun in circular mode, slow consumer | Process each half in time; count overruns |
| Two peripherals interfere | Request conflict on one stream | Remap to different streams or controllers |

## Quick selection guide

| Need | Use |
|---|---|
| Move a block once | Normal mode, completion interrupt |
| Continuous sampling or reception | Circular mode with half and full callbacks |
| Ping-pong without gaps | Double-buffer mode where supported, or circular with two halves |
| Memory to memory | A controller that supports it (check the part), or a software copy |
| Peripheral on a cached core | Non-cacheable buffer region, or explicit cache clean and invalidate |

## Tips

1. **Nothing happens**: the peripheral's own DMA enable bit, or the request mapping.
2. **Data wrong on cached cores**: cache clean and invalidate, alignment to the cache line.
3. **Transfer error flag**: wrong address region, unsupported width or alignment.
