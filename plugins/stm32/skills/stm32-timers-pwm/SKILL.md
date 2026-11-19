---
name: stm32-timers-pwm
description: Configure and debug STM32 timers: prescaler and auto-reload calculation, timer clock doubling rules, PWM generation with preload, complementary outputs with dead time for motor and power stages, input capture, encoder interface, one-pulse mode, periodic interrupts, timer-triggered ADC, and low-power timers. Use when a PWM frequency or duty is wrong, outputs do not appear, a time base must be exact, or events must be measured. Trigger with "STM32 timer", "PWM frequency", "PWM not outputting", "dead time", "input capture", "encoder mode", "timer interrupt rate", "advanced timer".
argument-hint: "<frequency, resolution, channels, features needed, or the symptom>"
---

# /stm32:stm32-timers-pwm

Configure STM32 timers and PWM with correct frequency, resolution, and outputs.

## Usage

```
/stm32:stm32-timers-pwm $ARGUMENTS
```

If details are missing, ask for the part and timer instance, the timer clock, target frequency and resolution, number of channels, and whether complementary outputs, dead time, or synchronization are needed.

## Workflow

1. **Find the real timer clock** (bus clock, with the doubling rule for the family) and the timer width (16 or 32 bit).
2. **Compute prescaler and auto-reload** for the frequency and resolution; show the result and the error.
3. **Pick the pins and channels** from the datasheet alternate-function table.
4. **Configure the mode** (PWM, capture, encoder, one-pulse), preload, polarity, and outputs; for advanced timers enable the main output and set dead time and break.
5. **Verify** the waveform on a scope: frequency, duty, polarity, dead time, and startup behavior.

Details, configuration checklists, example code, and failure modes are in `references/timers-pwm-config.md`.

## Choosing an approach

| Need | Use |
|---|---|
| Periodic interrupt or time base | Update event with an interrupt |
| PWM with glitch-free updates | Preload enabled on the auto-reload and compare registers |
| Half-bridge or motor drive | Complementary outputs with dead time and a break input |
| Measure pulse width or frequency | Input capture, with DMA for high rates |
| Quadrature encoder | Encoder interface mode with input filtering |
| Synchronize ADC sampling to PWM | Timer trigger output to the ADC |

## Output

```markdown
## Timers and PWM Plan: [context]

### Timer calculation (clock, prescaler, reload, frequency, resolution, error)
- [..]

### Channel and pin plan
- [..]

### Safety plan for power stages (dead time, break, startup state)
- [..]

### Verification steps
- [..]
```

## Rules

- Always compute from the real timer clock, not the bus clock.
- For power stages, define a safe state for reset, debug halt, and fault before enabling outputs.
- Check the maximum frequency and resolution trade-off: more resolution lowers the achievable frequency.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **No PWM output**: check the pin AF, the channel enable, and for advanced timers the main output enable.
2. **Frequency off by a factor of two**: the timer clock doubling rule.
3. **Duty glitches**: update compare values with preload enabled.
