---
name: stm32-gpio-exti
description: Configure STM32 GPIO pins and external interrupts (EXTI): input, output, alternate function, analog modes, pull and speed settings, pin-change interrupts, debouncing, wake-up from low-power modes, and pin-level failures. Use when setting up buttons, LEDs, chip selects, or interrupt lines, mapping EXTI lines to ports, or debugging a pin that does not toggle, reads wrong, or triggers spurious interrupts. Trigger with "STM32 GPIO", "EXTI not firing", "button interrupt", "pin conflict", "alternate function", "debounce", "pin not toggling".
argument-hint: "<pin function, mode, edge and wake needs, or the symptom>"
---

# /stm32:stm32-gpio-exti

Plan and troubleshoot STM32 pin configuration and pin-change interrupts.

## Usage

```
/stm32:stm32-gpio-exti $ARGUMENTS
```

If details are missing, ask for the part, the pin, the signal direction and level, the edge to detect, and whether the pin must wake the device.

## Workflow

1. **Identify the role**: input, push-pull or open-drain output, alternate function, or analog.
2. **Check the pin** in the datasheet: alternate-function table, 5 V tolerance, drive strength, and reserved functions.
3. **Configure** mode, pull, speed, and alternate function; enable the port clock first.
4. **For interrupts**: map the pin to its EXTI line, choose edges, set the priority, and handle the pending flag in the handler or callback.
5. **Verify** with a scope or by reading the input register; check for line conflicts and bounce.

Details, configuration checklists, example code, and failure modes are in `references/gpio-exti.md`.

## Choosing an approach

| Need | Use |
|---|---|
| Set or clear a pin from an ISR and the main loop without a race | Atomic set and reset register (bit set/reset), not read-modify-write on the output register |
| Button input | Pull-up or pull-down, EXTI on the active edge, software debounce timer |
| Drive an I2C-like bus line | Open-drain output with an external pull-up |
| Lowest leakage for unused pins | Analog mode |
| Wake from Stop | EXTI line enabled as interrupt or event; clear the wake flag |

## Output

```markdown
## GPIO and EXTI Plan: [context]

### Pin table (pin, function, mode, pull, speed, AF)
- [..]

### EXTI plan (line, port, edge, priority, handler)
- [..]

### Verification steps
- [..]
```

## Rules

- Take alternate-function numbers from the datasheet, not from memory.
- Enable the GPIO port clock before configuring the pin.
- Keep interrupt handlers short; defer work.
- Confirm register-level and family-specific details against the reference manual, datasheet, and errata sheet for the exact part.

## Tips

1. **Only one port per EXTI line number**: PA0 and PB0 cannot both use line 0.
2. **Debounce** in software with a timer or in hardware with a filter; do not delay inside the ISR.
3. **Keep SWD pins** free unless you accept losing the debugger.
