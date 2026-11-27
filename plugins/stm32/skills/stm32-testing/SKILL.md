---
name: stm32-testing
description: Plan tests and CI for STM32 firmware: host unit tests against a mocked port layer, on-target and hardware-in-the-loop tests, fault injection, static analysis, and a build pipeline.
argument-hint: "<project or module to test, toolchain, CI system>"
disable-model-invocation: true
---

# /stm32:stm32-testing

Produce a test strategy and CI setup that fits the firmware's modules and the hardware available.

If the project has architecture documents, derive tests from the module contracts instead of reading code.

## Steps

1. **Inputs**: module contracts (or the code layout), toolchain, CI system, available hardware (boards, probes, test fixtures), and what failures matter most.
2. **Choose the layers** with the table below; push as much as possible to host tests.
3. **Derive tests per module** from its contract: normal path, error and timeout paths, boundary values, concurrency assumptions (who calls from which context).
4. **Plan the port seam**: drivers depend on a small bus-port interface that tests replace with a fake (see `references/testing-and-ci.md`).
5. **Plan CI**: build for the target, run host tests, static analysis, size and stack reports, artifact archive.
6. **Plan hardware tests**: what runs on the board, how results come back, and what a test rig must provide.

## Layers

| Layer | Runs on | Covers | Limits |
|---|---|---|---|
| Host unit tests | PC | Pure logic, protocol parsing, state machines, drivers via a fake port | No timing, no real peripherals |
| On-target tests | Board | Peripheral setup, DMA, interrupts, timing | Needs a board and a way to report results |
| Hardware-in-the-loop | Rig | End-to-end behavior with real devices and stimuli | Setup effort, slower |
| Static analysis and builds | CI | Warnings, MISRA or CERT rules, size growth | Does not prove behavior |
| Soak and fault injection | Rig or board | Resets, bus errors, power loss, long runs | Needs time and instrumentation |

## Output

```markdown
## Test Plan: [project]

| Module | Layer | Tests | Fake or fixture needed |
|---|---|---|---|

### CI pipeline
- [stages and tools]

### Hardware rig
- [what it needs]

### Gaps
- [untested risks]
```

## Rules

- Do not rely on tests that need hardware where a host test would do.
- State what each test cannot prove; passing host tests do not prove timing or electrical behavior.
- Pin tool and library versions in CI.
