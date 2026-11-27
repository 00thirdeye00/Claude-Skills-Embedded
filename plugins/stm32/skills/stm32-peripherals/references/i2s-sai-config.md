# STM32 audio (I2S and SAI)

I2S and SAI features and clock options differ by family. Confirm in the reference manual and the codec datasheet.

## Setup checklist
- **Format**: I2S (Philips), left- or right-justified, or PCM/TDM; the codec and the MCU must match on format, word length, and frame length.
- **Clocks**: audio needs an accurate sample rate. Derive it from a dedicated audio PLL or kernel clock where the family has one, and compute the achieved rate and error; some sample rates cannot be reached exactly from a general system clock. Provide the master clock (MCLK) to the codec if it needs one.
- **Master or slave**: decide who generates the bit and frame clocks; a codec as master avoids rate errors on the MCU side.
- **Data**: 24-bit samples usually travel in 32-bit slots; match the DMA data width to the slot size and the buffer layout (left and right interleaved).
- **DMA**: circular transfers with half and full callbacks (double buffering); keep the processing time per half buffer below the half-buffer duration.
- **Codec control**: configure the codec over I2C or SPI before starting the audio stream; follow its power-up sequence and mute handling.
- **Cached cores**: buffers in DMA-reachable, cache-safe memory.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| No sound | Codec not configured, wrong format or slot, mute | Decode bit clock, frame sync, and data on a logic analyzer |
| Pitch wrong or drifting | Sample rate error, clock source | Compute the achieved rate; measure the frame sync frequency |
| Clicks and pops | Buffer underrun or overrun, processing too slow, priority | Underrun counters, callback timing |
| Left and right swapped or noisy | Frame sync polarity or alignment | Compare with the codec timing diagram |
| Distortion | Word length or alignment mismatch, gain | Check slot size and justification |
