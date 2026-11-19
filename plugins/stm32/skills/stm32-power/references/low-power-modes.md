# STM32 low-power modes

Mode names, variants, and exact behavior differ by family. Read the Power chapter of the reference manual and the electrical characteristics in the datasheet for the exact part.

## Contents
- Mode overview
- Entry and exit sequence
- RTOS tick and tickless idle
- Measuring current
- Common problems

## Mode overview

| Mode | Core | Clocks and peripherals | State retention | Typical wake sources |
|---|---|---|---|---|
| Run (reduced clock) | Running | Selectable | All | None needed |
| Sleep | Stopped | Peripherals keep running | All | Any enabled interrupt |
| Stop (variants on some families) | Stopped | Most clocks stopped | RAM and registers retained | External lines, RTC, low-power timers and UART, others by family |
| Standby | Off | Mostly off | Little; optional retained RAM and the backup domain on some parts | Wake-up pins, RTC, watchdog, reset |
| Shutdown (some families) | Off | Lowest consumption | Backup domain only | Wake-up pins, RTC |

After a wake from Stop, the system clock typically reverts to an internal oscillator, so restore the clock tree. After Standby or Shutdown the device restarts like a reset; check the reset and wake flags to see why it started.

## Entry and exit sequence

1. Finish or park ongoing transfers; stop DMA that must not run; disable peripherals that do not need to run.
2. Configure wake sources and enable their interrupt or event lines.
3. Clear wake-up and pending flags so the device does not wake immediately.
4. Set GPIOs to a state that avoids leakage and contention.
5. Suspend or reconfigure the system tick if it would wake the core.
6. Enter the mode with the HAL power API or by setting the deep-sleep bit and executing a wait instruction (`WFI` for interrupts, `WFE` for events).
7. On wake: restore the clock tree and voltage scaling, re-enable peripherals and the system tick, and re-check state that was not retained.

## RTOS tick and tickless idle

The core's system tick timer stops in deep modes, so the RTOS tick must come from a timer that keeps running in the chosen mode (a low-power timer or the RTC). Kernels offer a tickless idle mode in which the kernel computes the idle time, programs the wake-up timer, enters the low-power mode, and corrects the tick count after wake-up. Test that the wake-up time and the clock restoration fit within the kernel's assumptions.

## Measuring current

- Use a meter or analyzer with enough range and speed for the current profile; average multimeters miss short bursts.
- Remove or isolate debug probes, power LEDs, and other board loads. Many development boards expose a jumper in the supply path for measurement.
- Measure after the system has settled, and with the final firmware (clocks, pin states).
- Compare against the datasheet's conditions: temperature, supply voltage, which peripherals are enabled.

## Common problems

| Symptom | Likely cause | Check |
|---|---|---|
| Wakes immediately | Pending interrupt or event, stale wake flag, system tick still running | Clear flags, disable the tick, check pending registers |
| Never wakes | Wake source not armed, line not routed, wrong event versus interrupt choice | Verify the wake-source configuration and the pin or timer state |
| Debugger disconnects in sleep | Debug clocks off in low power | Enable debug in low-power modes during development only |
| High sleep current | Floating or driven pins, external pull-ups, enabled peripheral clocks, regulator mode, leakage through connected devices | Set pins to analog, disable clocks, check external circuitry and regulator settings |
| Peripherals wrong after wake | Clock restore incomplete, registers lost | Re-initialize after wake; verify retention in the manual |
| Resets after wake from Standby | Treating wake as a resume instead of a reboot | Check reset flags; design for restart |
