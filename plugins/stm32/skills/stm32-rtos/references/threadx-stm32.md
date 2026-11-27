# ThreadX on STM32

ThreadX (now maintained as Eclipse ThreadX; earlier Azure RTOS ThreadX) is available for STM32 through vendor packages and the open-source repository. APIs and package names change between releases; check the version in use.

## Structure
- `main` initializes the board and HAL, then calls `tx_kernel_enter()`. The kernel then calls your `tx_application_define(void *first_unused_memory)`, where you create byte pools, threads, queues, semaphores, mutexes, event flags, and timers.
- The port uses the core's PendSV for context switching and the system tick timer for the kernel tick, set up in the low-level initialization. Move the HAL time base to another timer if the system tick belongs to the kernel.

## Key points
- **Priorities**: lower numbers are higher priority; the default range is 0 to 31.
- **Create a thread**: `tx_thread_create(&t, "name", entry, input, stack_ptr, stack_size_bytes, priority, preempt_threshold, time_slice, TX_AUTO_START)`. Stack sizes are in bytes.
- **Preemption-threshold** reduces context switches among cooperating threads; use it deliberately.
- **Memory**: byte pools (variable size) and block pools (fixed size) allocate from memory you provide; size them from measurement and check return codes.
- **Mutexes** support priority inheritance when created with the inherit option; use them for shared resources.
- **ISRs**: service calls from interrupt handlers must not wait (use the no-wait option). Check the port documentation for the interrupt masking method (global mask or base-priority) and any priority limits.
- **Stack checking**: enable the stack-checking build option during development.

## Failure modes
| Symptom | Likely cause | Check |
|---|---|---|
| Hang in startup | Pool too small, `tx_application_define` returns an error, tick not running | Return codes, pool sizes, tick timer setup |
| Random corruption | Stack overflow | Stack checking, stack sizes in bytes |
| Missed deadlines | Priority assignment, time-slicing, ISR time | Priorities, thread timing |
| HAL timeouts hang | HAL time base conflicts with the kernel tick | Separate HAL timer |
