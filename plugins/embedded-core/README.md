# embedded-core plugin

Platform-independent embedded systems skills: ISR and concurrency rules, RTOS concepts and schedulability, bus protocol theory, and generic firmware review, debug, and release checklists. Companion to the platform plugins in this repository, such as `stm32`.

## Workflows and references

All skills are started by you with a command; none loads on its own (in Claude Code), so they add no tokens until you call them.

- **Workflow**: a fixed procedure that ends in a deliverable (report, checklist).
- **Reference**: lookup knowledge for one topic.

### Workflows

| Command | Use it when |
|---|---|
| `/embedded-core:embedded-orchestrator` | You have a multi-stage goal on a non-STM32 MCU: it plans, waits for approval, runs the generic skills, and logs gaps (for STM32 use `/stm32:stm32-orchestrator`) |
| `/embedded-core:embedded-isr-concurrency` | An ISR shares data with the main loop or a task, or you suspect a race |
| `/embedded-core:embedded-rtos-concepts` | Designing tasks, priorities, IPC, stack sizes, or checking deadlines |
| `/embedded-core:embedded-review` | Reviewing firmware for a non-STM32 target, or generic items |
| `/embedded-core:embedded-debug` | An intermittent or timing-dependent bug on any MCU |
| `/embedded-core:embedded-release` | A go/no-go checklist for shipping firmware |

### Reference

| Command | Covers |
|---|---|
| `/embedded-core:embedded-protocols` | I2C, SPI, UART and RS-485, CAN and CAN FD, USB: theory, sizing, failure modes (one bus reference loaded per use) |

## How to run them

```
/embedded-core:embedded-protocols I2C pull-up for 400 kHz with 120 pF bus capacitance
/embedded-core:embedded-review <paste the diff>
```

For several tasks, send one command per message.

## When to use it, when to skip it

Skip it for quick questions. Use it for non-STM32 targets or when you want the generic checklists. For STM32 targets prefer the `stm32-` versions of review, debug, and release, and do not run both on the same change.

## Accuracy

Protocol and architecture facts follow the relevant specifications and the Arm architecture; verify vendor-specific behavior and numeric limits against the datasheet and reference manual of your part.

## License

MIT. See `LICENSE`.
