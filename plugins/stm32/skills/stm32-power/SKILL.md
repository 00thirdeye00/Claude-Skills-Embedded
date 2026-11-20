---
name: stm32-power
description: Plan and debug STM32 low-power operation: mode choice, wake sources, tickless idle, current budget, and measurement.
argument-hint: "<power goal or battery, active duty cycle, wake sources, or the symptom>"
disable-model-invocation: true
---

# /stm32:stm32-power

Plan low-power operation and diagnose power problems on STM32 devices.

If details are missing, ask for the part number, supply and battery capacity, the active and idle time profile, required wake-up sources and latency, and whether an RTOS is used.

## Steps

1. **Build the activity profile**: what must run, how often, and how quickly the system must respond.
2. **Choose a mode** using `references/low-power-modes.md`: the deepest mode whose retained state, wake sources, and wake-up time fit.
3. **Write the entry and exit sequence**: stop or park peripherals, clear stale wake flags, arm wake sources, configure GPIOs, enter the mode, and on wake restore clocks, power, and peripherals.
4. **Handle the RTOS**: the system tick stops in deeper modes, so use a low-power timer or the RTC for the tick, with the kernel's tickless idle support.
5. **Estimate the budget**: `I_avg = sum(I_mode * t_mode) / T`, and battery life as usable capacity divided by `I_avg`, with a derating margin for temperature and aging.
6. **Measure and chase**: use a proper current measurement, then find unexpected loads.

## Output

```markdown
## Low-Power Plan: [product]

### Profile
| State | Duration | Current (est.) |
|---|---|---|

### Mode choice
[mode, retained state, wake sources, wake time]

### Sequence
[entry and exit steps]

### Budget
- Average current: [value]; battery life: [value] (with [margin])

### Measurement plan
- [setup, expected values, checks]
```

## Rules

- Take mode currents and wake times from the datasheet for the exact part and conditions; treat any other number as an estimate.
- State what is lost in each mode (registers, RAM, peripheral state) and how it is restored.
- Never lock out the debugger without telling the user how to recover access.

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
