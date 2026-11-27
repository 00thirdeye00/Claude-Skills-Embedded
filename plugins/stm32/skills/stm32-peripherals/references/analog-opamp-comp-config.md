# STM32 operational amplifiers and comparators

OPAMP and COMP blocks and their internal connections differ by family. Confirm in the reference manual and the electrical characteristics.

## Operational amplifier (OPAMP)
- Modes typically include standalone, follower, and programmable gain (PGA), with internal routing to the ADC or comparators in some modes. Choose the mode from the circuit: sensor buffering, current-sense gain, or signal conditioning.
- Respect input and output voltage ranges, gain-bandwidth, slew rate, and settling time from the datasheet; the output cannot swing to the rails.
- Run the trimming or calibration routine if the family provides it, and enable the power mode that matches the needed speed.
- Pair with the ADC: the amplifier's output settling and the ADC's sampling time must be compatible with the source impedance.

## Comparator (COMP)
- Select the inputs (external pins, DAC outputs, or internal references), the polarity, the hysteresis, and the power and speed mode.
- A comparator can generate an interrupt or event, wake the device, or drive a timer break or blanking input for fast protection (for example overcurrent).
- Use blanking from a timer to ignore switching noise at known instants.
- Add hysteresis to avoid chatter near the threshold; set the threshold from the DAC or the internal reference with the accuracy the datasheet gives.

## Typical uses
- Current sensing: shunt, amplifier in PGA mode, ADC sampled at the PWM center, comparator for hardware overcurrent trip.
- Zero-cross detection: comparator with hysteresis feeding a timer capture.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| Output clipped or offset | Output swing limits, input range, no calibration | Check ranges, run calibration |
| Noisy readings | Bandwidth, layout, sampling at switching edges | Filter, sample in quiet windows |
| Comparator chatters | No hysteresis, noise | Add hysteresis, blanking |
| Protection too slow | Using interrupt path instead of the direct timer break | Route to the break input |
