---
name: embedded-debug
description: Run a platform-independent firmware debugging session: reproduce, instrument, isolate, diagnose, and guard.
argument-hint: "<symptom, when it happens, what has been tried>"
disable-model-invocation: true
---

# /embedded-core:embedded-debug

Run a disciplined debugging session for firmware problems where the cause is not obvious.

If no symptom is given, ask what happens, what should happen, how often, and what changed recently.

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

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
