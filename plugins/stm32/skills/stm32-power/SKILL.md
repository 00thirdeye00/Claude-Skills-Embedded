---
name: stm32-power
description: Design and debug low-power behavior on STM32: choose between Sleep, Stop, Standby, and Shutdown modes, select wake sources, restore clocks and peripherals after wake-up, handle the RTOS tick with tickless idle, estimate battery life, and find why measured current is too high. Use when battery life is a goal, when the device will not enter or wake from a low-power mode, or when current in sleep is higher than the datasheet. Trigger with "STM32 low power", "enter stop mode", "wakes up immediately", "won't wake from standby", "current too high in sleep", "battery life estimate", "tickless idle".
argument-hint: "<power goal or battery, active duty cycle, wake sources, or the symptom>"
---

# /stm32:stm32-power

Plan low-power operation and diagnose power problems on STM32 devices.

## Usage

```
/stm32:stm32-power $ARGUMENTS
```

If details are missing, ask for the part number, supply and battery capacity, the active and idle time profile, required wake-up sources and latency, and whether an RTOS is used.

## How It Works

```
┌──────────────────────────────────────────────────────────┐
│ 1 PROFILE   active/idle timeline, wake needs, latency     │
│ 2 MODE      pick the deepest mode that meets the needs    │
│ 3 SEQUENCE  quiesce, arm wake, enter, restore             │
│ 4 BUDGET    average current and battery life estimate     │
│ 5 MEASURE   verify, then chase leakage and stray loads    │
└──────────────────────────────────────────────────────────┘
```

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

## Tips

1. **Pending interrupts** cause immediate wake; clear flags before entering.
2. **Floating or driven pins** often dominate sleep current; set unused pins to analog and check external pull-ups and LEDs.
3. **Debugger and probe circuits** add current; measure with them disconnected.
