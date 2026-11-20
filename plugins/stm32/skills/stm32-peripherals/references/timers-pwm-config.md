# STM32 timers and PWM configuration

Timer features, widths, and clock rules vary by family and instance. Check the reference manual and the datasheet.

## Contents
- Frequency and resolution
- Timer clock
- PWM
- Advanced timers
- Input capture and encoder
- Interrupts and DMA
- Synchronization
- Failure modes
- Quick selection guide
- Tips

## Frequency and resolution

```
f_update = f_timer / ((PSC + 1) * (ARR + 1))
duty = CCR / (ARR + 1)           (edge-aligned PWM)
```

The prescaler (PSC) and auto-reload (ARR) values are written as the desired value minus one. More resolution (larger ARR) lowers the maximum frequency. Example: a 72 MHz timer clock, 1 kHz PWM with 1000 steps: PSC = 71 gives 1 MHz, ARR = 999 gives 1 kHz, and a duty of 25 percent is CCR = 250.

Counter width is 16 bits on most timers and 32 bits on a few; the limit constrains the longest period.

## Timer clock

The timer clock is derived from the bus clock. On many families, when the bus prescaler is not 1, the timer clock is twice the bus clock; some families have an additional selection bit. Check the clock tree in the reference manual and compute from the actual timer clock. A frequency off by exactly a factor of two usually means this rule was missed.

## PWM

- Select PWM mode 1 or 2, set polarity, and enable the channel output.
- Enable preload on the compare register and the auto-reload register so updates take effect at the next period boundary without glitches. Write new duty values with the compare-set macro or function.
- Center-aligned mode counts up and down, halving the frequency for the same ARR, and is used where symmetric pulses matter.
- HAL examples: `HAL_TIM_PWM_Start`, `__HAL_TIM_SET_COMPARE`; for complementary outputs `HAL_TIMEx_PWMN_Start`.

## Advanced timers

- The main output enable (break and dead-time register) must be set for outputs to appear; HAL start functions set it, but register-level code must do it explicitly.
- Complementary outputs with dead time prevent shoot-through in half bridges. Compute dead time from the gate-driver and transistor switching times plus margin.
- A break input forces outputs to a defined state on a fault; configure its polarity and the idle states for the outputs.
- Define output idle states so the power stage is safe in reset, debug halt, and fault conditions.

## Input capture and encoder

- Capture timestamps edges for period and pulse-width measurement; handle counter overflow with an update-event count, or use a 32-bit timer.
- Use input filtering to reject noise, and DMA for high rates.
- Encoder interface mode counts quadrature signals in hardware; set the filter and handle counter wrap-around by reading it as a signed difference.

## Interrupts and DMA

- Update event interrupts give a periodic tick; keep handlers short.
- Timer DMA requests can update compare registers for waveform generation, or move captured values.
- Clear flags and use the callback structure of the HAL, or handle flags directly in register-level code.

## Synchronization

Timers can trigger each other and the ADC through their trigger output, which allows deterministic phase relationships between PWM channels and sampling. Configure master and slave modes and the trigger source selection as listed in the reference manual.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| No PWM output | Pin AF wrong, channel disabled, main output not enabled, clock gated | Check AF, channel enable, break and dead-time register, clock enable |
| Frequency wrong | Timer clock assumption, PSC or ARR off by one | Compute from the real timer clock; check the minus-one rule |
| Duty glitches | Preload disabled | Enable preload; update at the period boundary |
| Complementary outputs overlap | Dead time too small or not set | Set and verify dead time on a scope |
| Counter overflows when capturing | 16-bit range exceeded | Count update events or use a 32-bit timer |
| Output active after reset or halt | Idle state or debug-freeze behavior not configured | Configure idle states and debug freeze |

## Quick selection guide

| Need | Use |
|---|---|
| Periodic interrupt or time base | Update event with an interrupt |
| PWM with glitch-free updates | Preload enabled on the auto-reload and compare registers |
| Half-bridge or motor drive | Complementary outputs with dead time and a break input |
| Measure pulse width or frequency | Input capture, with DMA for high rates |
| Quadrature encoder | Encoder interface mode with input filtering |
| Synchronize ADC sampling to PWM | Timer trigger output to the ADC |

## Tips

1. **No PWM output**: check the pin AF, the channel enable, and for advanced timers the main output enable.
2. **Frequency off by a factor of two**: the timer clock doubling rule.
3. **Duty glitches**: update compare values with preload enabled.
