---
name: embedded-rtos-concepts
description: Design or review an RTOS task architecture: tasks, priorities, IPC choice, stack sizing, and schedulability.
argument-hint: "<system description, task list with periods and runtimes, or the problem>"
disable-model-invocation: true
---

# /embedded-core:embedded-rtos-concepts

Design or review the task architecture of an RTOS-based system: tasks, priorities, communication, stack sizes, and timing guarantees.

If no system is described, ask for the activities the firmware must perform, their rates or deadlines, and the RTOS in use.

## Workflow

1. **List activities** with trigger (periodic, interrupt, request), period or deadline, and worst-case execution time.
2. **Decompose into tasks.** One task per independent timing or blocking concern. Merge activities that always run together. Avoid one task per peripheral by reflex.
3. **Assign priorities.** Rate-monotonic for periodic work (shorter period, higher priority). Put short, latency-critical handlers high and long batch work low. Keep ISRs above all tasks.
4. **Pick communication primitives** with the table below. Prefer one-way data flow.
5. **Size stacks** and check heap use (see `references/rtos-sizing-and-analysis.md`).
6. **Check schedulability** with utilization and response-time analysis.
7. **Report** with the output template.

## Choosing a primitive

| Need | Use |
|---|---|
| Pass data items between tasks or from an ISR | Queue (copies data; bound the depth) |
| ISR or task signals "something happened" to one task | Task notification or binary semaphore |
| Count events or resource units | Counting semaphore |
| Protect a shared resource | Mutex (with priority inheritance), never a binary semaphore |
| Wait on several conditions | Event group or event flags |
| Byte stream with one writer and one reader | Stream or message buffer |
| Periodic or delayed callback | Software timer, with a short non-blocking callback |

Primitive names differ between kernels; map the role, not the name.

## Output

```markdown
## RTOS Design: [system]

### Tasks
| Task | Trigger | Period/deadline | WCET | Priority | Stack |
|---|---|---|---|---|---|

### Communication
[who sends what to whom, with which primitive and depth]

### Timing check
- Utilization: [value] vs bound [value]
- Worst-case response per task: [values] vs deadlines

### Risks
[priority inversion, deadlock, stack, heap, tick resolution]
```

## Rules

- Never call blocking APIs from an ISR or a timer callback.
- Take locks in a fixed global order to avoid deadlock; hold them briefly.
- State assumptions about execution times and mark them as estimates until measured.
- Prefer static allocation of kernel objects over the heap in long-running firmware.

## Connectors

Optional (see `CONNECTORS.md`): when `~~source control`, `~~project tracker`, or `~~knowledge base` is connected, use it for diffs, tickets, and datasheets.
