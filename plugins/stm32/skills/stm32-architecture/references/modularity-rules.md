# Modularity rules for STM32 firmware

## Contents
- Layers
- Interfaces
- Resources and ownership
- Concurrency
- Initialization
- Generated code
- Suggested layout

## Layers

| Layer | Contains | May depend on |
|---|---|---|
| Board support (bsp) | Clock and pin setup, HAL port, board constants | Vendor HAL or LL |
| Drivers | One module per external chip or peripheral instance | bsp |
| Services | Protocol stacks, storage, logging, communication, update logic | drivers, bsp |
| Application | Tasks, state machines, product behavior, startup wiring | services, drivers |

Dependencies point downward only. A lower layer never calls up; use callbacks or events registered by the upper layer.

## Interfaces

- One public header per module is the contract. Everything else is private.
- Hide the handle: use an opaque type or a struct created and owned by the module.
- HAL calls live only in the board support or in a thin port file of the driver, never in services or the application.
- No shared global variables between modules; expose functions.
- Every public function states: blocking or not, allowed contexts (task, ISR, both), timeouts, and error codes.

## Resources and ownership

- Every pin, DMA channel, timer, interrupt priority, bus, and memory region has exactly one owner module, recorded in the resource map.
- A shared bus has one owner that serializes access (a lock or a queue); devices on it do not take the bus directly.
- Interrupt priorities are assigned from the central table, not chosen per module.

## Concurrency

- State which task or interrupt calls each function, and which data is shared.
- An ISR does the minimum and hands work to a task through a queue, notification, or flag owned by the module.
- RTOS objects (tasks, queues, mutexes) are created and owned by the module that uses them, with static allocation.

## Initialization

- One startup function sequences module initialization in dependency order and handles failures. Modules do not initialize each other implicitly.
- Hardware init failures are reported with an error code and a defined safe state.

## Generated code

- CubeMX or vendor-generated files stay in their own directories. Hand-written code goes in user sections or in separate files, so regeneration does not destroy it.
- The board support layer wraps generated handles; upper layers do not include generated headers.

## Suggested layout

```
CLAUDE.md
docs/architecture/ARCHITECTURE.md
docs/architecture/modules/<module>.md
Core/ and Drivers/          generated vendor code, not hand-edited
src/bsp/
src/drivers/<chip>/         <chip>.h (contract), <chip>.c, <chip>_port.c
src/services/<name>/
src/app/                    tasks, startup wiring, main
tests/
```
