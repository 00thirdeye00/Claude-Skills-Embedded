# STM32 displays (LTDC, DMA2D, and parallel or SPI panels)

Display controller availability depends on the family. Confirm in the reference manual and the panel datasheet.

## LTDC setup checklist
- **Timing**: take the pixel clock, horizontal and vertical resolution, sync widths, front and back porches, and polarities from the panel datasheet. The LTDC timing registers hold the sums and offsets; compute them carefully and check the achieved refresh rate.
- **Pixel clock**: generate it from a dedicated PLL output and keep it within the panel and controller limits.
- **Framebuffer**: place it in external or internal RAM with enough bandwidth. The LTDC reads the framebuffer continuously, so memory bandwidth must cover the pixel clock times bytes per pixel plus the CPU and DMA traffic.
- **Layers and formats**: choose pixel formats per layer (for example 16-bit RGB or 32-bit ARGB), layer windows, blending, and color keys as the design requires.
- **Double buffering**: draw into the back buffer and swap on the vertical blanking interrupt to avoid tearing.
- **DMA2D**: use it for fills, copies, format conversion, and blending; on cached cores clean the cache after CPU writes and invalidate before CPU reads of DMA2D results.
- **MPU and cache**: external RAM used by the display may need specific cache attributes.
- **Backlight and power**: PWM for the backlight, panel power sequencing from the panel datasheet.

## Other interfaces
- **SPI panels**: simple but slow; use DMA with large transfers and partial updates.
- **Parallel panels over FMC**: the controller's address line selects command or data; set timings from the controller datasheet.
- **Graphics libraries** (such as TouchGFX or LVGL) need a flush callback, a framebuffer policy, and a tick; budget RAM and CPU early.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| Blank screen | Pixel clock, enable or backlight, timing, power sequence | Scope sync and clock, check backlight and panel power |
| Flicker or shimmer | Memory bandwidth, wrong porch values, supply noise | Memory load, timing values |
| Tearing | No vsync swap | Swap in the blanking interrupt |
| Wrong colors | Pixel format or byte order mismatch | Format settings and wiring order |
| Artifacts after CPU drawing | Cache not cleaned | Cache maintenance around the framebuffer |
