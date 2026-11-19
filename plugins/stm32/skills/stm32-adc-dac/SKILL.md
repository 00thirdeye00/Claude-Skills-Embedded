---
name: stm32-adc-dac
description: Configure and debug STM32 ADC and DAC: calibration, resolution and sampling time versus source impedance, reference voltage, internal channels (temperature sensor, internal reference), timer-triggered and DMA sampling, oversampling, noise reduction, and DAC output with DMA waveforms. Use when readings are noisy, offset, or wrong, when sampling at a fixed rate, computing VDDA or temperature, or generating analog waveforms. Trigger with "STM32 ADC", "ADC noisy", "ADC DMA", "ADC calibration", "ADC sampling time", "read temperature sensor", "VREFINT", "STM32 DAC".
argument-hint: "<signals, rates, source impedance, accuracy goals, or the symptom>"
---

# /stm32:stm32-adc-dac

Configure STM32 analog conversion and improve accuracy.

## Usage

```
/stm32:stm32-adc-dac $ARGUMENTS
```

If details are missing, ask for the part, signal sources and impedance, sample rate, resolution and accuracy needs, reference voltage, and a sample of bad readings.

## Workflow

1. **Characterize the signal**: range, bandwidth, source impedance, and accuracy goal.
2. **Choose the clock, resolution, and sampling time** from the datasheet source-impedance rule.
3. **Choose the trigger and data path**: software, timer trigger, DMA circular, or oversampling.
4. **Calibrate** at start-up where the family requires or supports it, and convert with the real reference voltage.
5. **Verify** with known inputs, and examine noise with a histogram or averaged samples.

Details, configuration checklists, example code, and failure modes are in `references/adc-dac-config.md`.

## Choosing an approach

| Need | Use |
|---|---|
| Occasional reading | Single conversion, polled or interrupt |
| Fixed-rate sampling | Timer trigger with DMA into a buffer, half and full callbacks |
| Several channels | Scan sequence with DMA, one sample time per channel |
| More resolution at low bandwidth | Hardware oversampling or averaging |
| Absolute accuracy with a varying supply | Measure the internal reference and compute the supply voltage |

## Output

```markdown
## ADC and DAC Plan: [context]

### Timing and accuracy table (ADC clock, sampling time, conversion time, source impedance check)
- [..]

### Trigger and DMA plan
- [..]

### Calibration and reference plan
- [..]

### Verification steps
- [..]
```

## Rules

- Check the source-impedance versus sampling-time rule using the datasheet formula.
- State the reference voltage used for the scaling and how it is measured.
- On cached cores, treat ADC DMA buffers like any DMA buffer.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **Noisy readings**: lengthen the sampling time, add a capacitor and a low-impedance buffer, and keep switching signals away.
2. **Wrong readings after power-up**: run calibration and wait for the ADC to stabilize.
3. **Channel crosstalk** happens with high-impedance sources in a scan; raise the sampling time.
