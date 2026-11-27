# STM32 watchdogs (IWDG and WWDG)

Names, clock sources, and options differ by family. Confirm in the reference manual and the option-byte description.

## Independent watchdog (IWDG)
- Runs from the low-speed internal oscillator, so it keeps running if the main clock fails. That oscillator is imprecise (a wide tolerance in the datasheet), so size the timeout with margin.
- Timeout is about `(reload + 1) * prescaler / f_LSI`. Choose the prescaler and reload from the longest healthy interval plus margin, using the worst-case oscillator frequency.
- Can be started by software or forced on by an option bit at reset (hardware mode). Hardware mode protects against firmware that never starts it.
- Once started it cannot be stopped; behavior in low-power modes and when the debugger halts the core is configurable or fixed by family.

## Window watchdog (WWDG)
- Clocked from the bus clock; resets if refreshed too early or too late (window). Has an early wake-up interrupt that can log state before the reset.
- Use it for timing-critical loops where a too-fast loop also signals a fault.

## Feeding policy
- Feed from one place that checks health: a supervisor task that verifies each critical task has reported progress since the last feed, not a timer interrupt that always feeds.
- Feed after the checks pass, not before. Keep long operations (flash erase, firmware update) in mind: lengthen the timeout or feed from the operation's loop.
- On a watchdog reset, record the cause (reset flags in the clock and reset controller), the last supervisor state, and a counter; limit repeated resets to a safe mode.

## Debugging
Debug settings can freeze watchdogs while the core is halted; check that the release configuration does not depend on that, and test with the debugger disconnected.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| Unexpected resets | Timeout too short for the worst case, long blocking operation, oscillator tolerance | Compute with the slowest LSI, measure the longest loop |
| Never resets on a hang | Fed from an interrupt or a healthy-looking task | Move feeding to the supervisor |
| Resets only without the debugger | Debug freeze hides it | Run without the probe |
| Reset loop after update | New firmware misses the first feed | Feed during init, lengthen the first timeout |
