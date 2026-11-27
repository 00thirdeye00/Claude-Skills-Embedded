# STM32 RTC and backup domain

RTC features, clock sources, and backup domain behavior differ by family. Confirm in the reference manual.

## Setup checklist
- **Clock source**: a 32.768 kHz crystal (LSE) for accuracy, or the internal low-speed oscillator (LSI), which is far less accurate and suited only to coarse timing. Select the source once; changing it needs a backup domain reset on many families.
- **Backup domain access**: enable access in the power controller before writing RTC or backup registers, and keep it enabled while configuring.
- **LSE start-up**: choose load capacitors from the crystal datasheet and the oscillator drive setting, wait for the ready flag with a timeout, and handle a failure by falling back or reporting it.
- **Initialization**: set prescalers, calendar, and format; detect first initialization with a marker in a backup register so a reset does not overwrite the time.
- **Wake-up and alarms**: the wake-up timer and alarms can wake from Stop and Standby; clear their flags and re-arm them before sleeping again.
- **Calibration**: use the digital calibration feature to trim the rate once you have measured the crystal's error.
- **Battery**: a battery or supercapacitor on the backup supply keeps the RTC and backup registers across power loss; verify the voltage range and what the reference manual says about reset sources.
- **Tamper**: tamper inputs can timestamp or erase backup data; configure them deliberately or leave them disabled.

## Accuracy
Timekeeping error in seconds per day is about 86400 times the frequency error in parts per million divided by one million: for example 20 ppm is about 1.7 seconds per day. Temperature shifts a crystal's frequency, so measure over the operating range if accuracy matters.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| Time resets every power cycle | No battery, domain reset, initialization overwrite | Marker register, supply on the backup pin |
| LSE never ready | Crystal, load capacitors, layout, drive strength | Scope the oscillator, compare with the datasheet |
| Time drifts | LSI used, uncalibrated crystal, temperature | Clock source, calibration |
| Cannot write RTC | Backup domain access not enabled | Power controller setting |
| Wake-up does not occur | Flag not cleared, wrong EXTI or wake source | Wake-up configuration and flags |
