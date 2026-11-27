# Extension checklist

## Contents
- Resource questions
- Common extensions
- When opening a .c file is justified

## Resource questions

Answer each from the resource map. A "yes" without an owner means a conflict to resolve before coding.

| Resource | Questions |
|---|---|
| Pins | Is the pin free? Does its alternate function match the peripheral and the datasheet? Is it shared with debug or boot? |
| Peripheral instance | Is it free, or owned by another module? Which mode and clock does it use? |
| Bus (I2C, SPI, UART) | Who owns the lock? Will the new device change timing, speed, or latency for the others? |
| DMA | Is the channel or request free? Is the buffer in a region this DMA can reach, and cache-safe? |
| Interrupts | Which priority fits the plan? Does it call the RTOS API (priority limit)? Does it preempt something time-critical? |
| Timers and clocks | Is the timer free? Does the change alter a shared clock, prescaler, or kernel clock? |
| Memory | Flash and RAM margin after the change? Any new buffer needing a special region? |
| RTOS | New task needed? Priority, stack size, and trigger? Which queue or notification connects it? |
| Power | Does the new feature change sleep behavior, wake sources, or peak current? |
| Init order | Does the new module need to start before or after another? |

## Common extensions

| Extension | Usually affects |
|---|---|
| New sensor on an existing bus | New driver module, the bus owner's contract, bus load and timing, application wiring |
| New communication channel | New service module, a peripheral and DMA, interrupt priority table, a task, power |
| New task or periodic job | Application module, RTOS table, stack and CPU budget |
| Change a peripheral mode or rate | Owner module, clocks, DMA, dependents of its data |
| Add storage or logging | New service, a bus or peripheral, flash wear and timing, task context |
| Change the clock tree | Board support, every timing-dependent module, baud rates, timer values |
| Add a bootloader or update path | Memory map, linker, startup, release process |

## When opening a .c file is justified

- The contract does not state a behavior you need (blocking, error codes, context) and the header does not answer it.
- A conflict in the resource map depends on code detail (for example which priority is really set).
- The documents and the code disagree and you must see which is right.

State the reason in the report, and propose a contract update so the next extension does not need the file.
