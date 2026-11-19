# Instrumentation techniques

## Contents
- GPIO toggling with a scope or logic analyzer
- Cycle counter
- Trace and logging
- Watchpoints
- Stack and heap checks
- Fault capture

## GPIO toggling with a scope or logic analyzer
Set a spare pin high at the start of the region and low at the end. A scope shows the duration, jitter, and worst case; a logic analyzer correlates it with bus activity. Use a direct register write to the pin (a single store) so the instrumentation costs a few cycles. Trigger on the pin, and use persistence or max-hold to catch rare long cases.

## Cycle counter
Cortex-M3 and up have a cycle counter in the DWT unit:

```c
CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;   /* enable trace/DWT */
DWT->CYCCNT = 0;
DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;
uint32_t t0 = DWT->CYCCNT;
/* ... code under test ... */
uint32_t cycles = DWT->CYCCNT - t0;               /* unsigned subtraction handles wrap */
```

On some Cortex-M7 devices the DWT registers must be unlocked first (`DWT->LAR = 0xC5ACCE55`). Cortex-M0 and M0+ have no cycle counter; use a hardware timer. Convert cycles to time using the actual core clock, and remember caches and flash wait states change results.

## Trace and logging
- Semihosting is slow and needs a debugger attached; avoid in timing-critical code.
- SWO/ITM output and RTT-style memory-based logging are fast and non-blocking compared with UART printing; they need a probe that supports them.
- Log to a RAM ring buffer with timestamps and dump it after the event; this suits intermittent bugs and has little timing impact.
- Count events (errors, overruns, retries) in volatile counters and inspect them with the debugger.

## Watchpoints
Hardware data watchpoints stop the CPU when an address is read or written. Use them to find who corrupts a variable, a stack guard word, or a pointer. The number of comparators is small (often 2 to 4 on Cortex-M); set them from the debugger or through the DWT unit.

## Stack and heap checks
- **Stack painting:** fill the stack with a known pattern (for example 0xA5A5A5A5) at start-up, run the workload, then scan from the far end for the first changed word to find the high-water mark.
- **Guard words** at the stack and buffer boundaries catch overflows; check them periodically or on fault.
- Where an MPU exists, a no-access region at the stack limit turns an overflow into an immediate fault.
- Check heap use and failed-allocation counters; fragmentation shows as allocation failure with free memory remaining.

## Fault capture
Install a fault handler that saves the stacked registers and fault status registers to retained RAM, then resets. After reset, report the saved record over the console or store it for upload. This turns field crashes into data. Resolve saved addresses with `addr2line` against the exact ELF of that build, so archive the ELF with every release.
