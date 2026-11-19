# embedded-core plugin

Platform-independent embedded systems skills: ISR and concurrency rules, RTOS concepts and schedulability, bus protocol theory, and generic firmware review, debug, and release checklists. It is the companion to the platform plugins, such as `stm32`, in this repository.

## Skills

| Skill | Use for |
|---|---|
| `embedded-isr-concurrency` | ISR rules, shared data, critical sections, ring buffers, interrupt latency |
| `embedded-rtos-concepts` | Task decomposition, priorities, IPC choice, stack sizing, schedulability analysis |
| `embedded-protocols` | I2C, SPI, UART and RS-485, CAN and CAN FD, USB: theory, sizing, failure modes |
| `embedded-review` | Firmware review checklist and report format |
| `embedded-debug` | Debugging method and instrumentation techniques |
| `embedded-release` | Release and update-safety checklist |

Invoke a skill as `/embedded-core:<skill-name>` (for example `/embedded-core:embedded-review`), or describe the task and Claude loads the matching skill.

## Accuracy

Protocol and architecture facts come from the relevant specifications and the Arm architecture; verify vendor-specific behavior and numeric limits against the datasheet and reference manual of your part.

## License

MIT. See `LICENSE`.
