# STM32 ADC and DAC configuration

ADC architecture, calibration, clocking, and channel features differ between families. Use the reference manual and the datasheet for the part.

## Contents
- Accuracy model
- Clock and timing
- Source impedance and sampling time
- Calibration and reference
- Trigger and DMA
- Internal channels
- Noise reduction
- DAC
- Failure modes
- Quick selection guide
- Tips

## Accuracy model

The converted value reflects the input, the reference voltage, gain and offset errors, noise, and the source's ability to charge the sampling capacitor in time. The datasheet lists offset, gain, linearity, and total unadjusted error under stated conditions, which are the limits to design against.

## Clock and timing

The ADC clock comes from a prescaled bus clock or a dedicated kernel clock, subject to a maximum frequency in the datasheet. Total conversion time is the sampling time plus a fixed number of cycles that depends on the resolution; take the cycle counts from the reference manual.

```
t_conv = (sampling_cycles + conversion_cycles) / f_ADC
max sample rate (single channel) = 1 / t_conv
```

## Source impedance and sampling time

The sampling capacitor must settle to the required accuracy during the sampling time. The datasheet gives the maximum source resistance as a function of the sampling time in a formula of this form:

```
R_AIN_max = Ts / (f_ADC * C_ADC * ln(2^(N+2))) - R_ADC
```

`Ts` is the sampling time, `N` the resolution in bits, `C_ADC` and `R_ADC` the internal sampling capacitance and resistance. Use the exact formula and values from your part's datasheet. If the source impedance is too high, increase the sampling time or add a buffer amplifier, or a capacitor at the pin that supplies the charge.

## Calibration and reference

- Run the calibration routine after power-up or after the ADC has been disabled, as the family requires (for example the HAL calibration function for the ADC), and before the first conversion. Recalibrate when the temperature or supply changes a lot.
- Scaling depends on the reference voltage (often the analog supply). If the supply varies, measure the internal reference channel and use the factory calibration value stored in the device to compute the actual analog supply: the factory value was measured at a stated supply voltage, so

```
VDDA = V_cal * VREFINT_CAL / VREFINT_DATA
```

where `V_cal` is the calibration voltage from the datasheet (commonly 3.0 V or 3.3 V), `VREFINT_CAL` the stored value, and `VREFINT_DATA` the measured value.

## Trigger and DMA

- Timer-triggered conversion gives a uniform sample rate: configure a timer to output a trigger on update, select it as the ADC external trigger, and set the edge.
- Use DMA in circular mode with half-transfer and complete callbacks to process blocks while the next fills. Pick a buffer size that makes the callback rate manageable.
- In scan mode, the sequence order sets the buffer layout; document it.
- On cached cores, handle the DMA buffer's cache like any other DMA buffer.
- Oversampling hardware averages several conversions and shifts the result, trading speed for resolution.

## Internal channels

The temperature sensor and the internal reference are internal channels. They need long sampling times as listed in the datasheet and may need enabling in the common control register. Temperature conversion uses two factory calibration points (often at 30 degrees and 110 degrees Celsius, at a stated supply voltage):

```
T = (T2 - T1) / (CAL2 - CAL1) * (data - CAL1) + T1
```

Take the calibration addresses, temperatures, and supply voltage from the datasheet.

## Noise reduction

- Filter the input with an RC low-pass matched to the bandwidth, and keep the source impedance low.
- Keep the analog supply clean with proper decoupling, and the analog ground separate or quiet.
- Avoid switching large currents or digital edges near analog inputs, and avoid transmitting on pins near the ADC input during sampling.
- Average several samples, or use oversampling.
- Sample at a point in the PWM or switching cycle where noise is low (timer-triggered sampling).

## DAC

- Output buffer: enable it for low-impedance drive; without it the output is high impedance and the available range differs.
- Triggered output and DMA allow waveform generation: a timer paces the DMA, which writes samples to the DAC data register.
- Allow the output settling time stated in the datasheet; the effective bandwidth and output step glitches follow from it.
- Use a reconstruction filter on waveform output.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| Readings offset or inconsistent | Not calibrated, source impedance too high, wrong reference | Calibrate; lengthen sampling time; measure the reference |
| Noisy values | Layout, supply noise, short sampling time | Add filtering, check decoupling, oversample |
| Channels influence each other | High source impedance in a scan | Raise sampling time or buffer inputs |
| Wrong temperature or supply value | Calibration voltage or sample time wrong | Use datasheet values and long sample times for internal channels |
| DMA data stale or mismatched | Cache coherency, buffer layout misunderstanding | Invalidate cache; check the scan order |
| Sample rate off | Timer clock or prescaler mistakes | Compute from the real timer clock |

## Quick selection guide

| Need | Use |
|---|---|
| Occasional reading | Single conversion, polled or interrupt |
| Fixed-rate sampling | Timer trigger with DMA into a buffer, half and full callbacks |
| Several channels | Scan sequence with DMA, one sample time per channel |
| More resolution at low bandwidth | Hardware oversampling or averaging |
| Absolute accuracy with a varying supply | Measure the internal reference and compute the supply voltage |

## Tips

1. **Noisy readings**: lengthen the sampling time, add a capacitor and a low-impedance buffer, and keep switching signals away.
2. **Wrong readings after power-up**: run calibration and wait for the ADC to stabilize.
3. **Channel crosstalk** happens with high-impedance sources in a scan; raise the sampling time.
