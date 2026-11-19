---
name: embedded-debug
description: Platform-independent debugging method for firmware on any MCU: reproduce, instrument, isolate, diagnose, fix. Use when firmware misbehaves in ways that are intermittent, timing-dependent, or only on hardware, when choosing between GPIO toggling, logic analyzer, trace, cycle counter, watchpoints, or stack painting, or when a platform-specific skill is not available. Trigger with "intermittent bug", "works sometimes", "how do I measure this timing", "memory corruption", "find stack usage", "random reset", "how to debug without a debugger".
argument-hint: "<symptom, when it happens, what has been tried>"
---

# /embedded-core:embedded-debug

Run a disciplined debugging session for firmware problems where the cause is not obvious.

## Usage

```
/embedded-core:embedded-debug $ARGUMENTS
```

If no symptom is given, ask what happens, what should happen, how often, and what changed recently.

## How It Works

```
┌──────────────────────────────────────────────────────────────┐
│ 1 REPRODUCE   make it happen on demand, note the conditions  │
│ 2 OBSERVE     add instrumentation with minimal disturbance   │
│ 3 ISOLATE     bisect code, hardware, configuration           │
│ 4 DIAGNOSE    one hypothesis, one confirming check at a time │
│ 5 FIX + GUARD fix the cause, add a regression check          │
└──────────────────────────────────────────────────────────────┘
```

## Steps

1. **Reproduce.** Record firmware version, hardware revision, supply, temperature, inputs, and timing. Find the shortest path to a failure. For intermittent bugs, build a stress loop or fault injection.
2. **Observe.** Pick the least intrusive tool from `references/instrumentation.md`: a GPIO pin with a scope, a logic analyzer decode, a cycle counter, trace output, a watchpoint, or stack painting. Heavy logging can hide timing bugs.
3. **Isolate.** Bisect by commit, by feature flag, by peripheral, by clock speed, or by optimization level. Swap hardware units to separate board faults from firmware faults.
4. **Diagnose.** Write the hypothesis and the check that would refute it. Run one check at a time. Read raw data, not summaries.
5. **Fix and guard.** Fix the root cause. Add an assert, a counter, a test, or a hardware watchpoint so a recurrence is caught early.

## Output

```markdown
## Debug Report: [summary]

### Reproduction
- [conditions, frequency, minimal steps]

### Evidence
- [captures, counters, register or memory dumps]

### Root cause
[chain from symptom to cause]

### Fix
[change]

### Guard
[assert, test, or monitor added]
```

## Rules

- Do not guess at the cause; name the next check instead.
- Change one variable at a time, and record each experiment.
- Distrust a fix that you cannot explain.
- Prefer measurement over reasoning when timing is involved.

## Tips

1. **A bug that vanishes when you add logging** is usually timing or a race; use a pin toggle instead.
2. **Check power and reset first** for random resets: brown-out, watchdog, and noisy supplies look like software bugs.
3. **Use the platform skill** (for example `/stm32:stm32-debug`) for fault-register decoding and family-specific causes.
