# FreeRTOS configuration for STM32

Names and defaults depend on the FreeRTOS version and the wrapper layer in use. Check the version's documentation and the port notes for your core.

## Contents
- Port selection
- Interrupt priorities
- Handler mapping
- HAL timebase
- Key configuration items
- Heap schemes
- Stack sizing and overflow
- Tickless idle
- Failure modes

## Port selection

Use the port directory that matches the core: M0 and M0+, M3, M4 with FPU (M4F), M7, M33 (with a non-secure or secure variant on parts with TrustZone). A port for a different core can start and then fault in unpredictable ways. The FPU port saves floating-point registers lazily; tasks that use the FPU need the larger context.

## Interrupt priorities

Cortex-M devices implement a limited number of priority bits (commonly 4 on STM32, giving 16 levels). A lower number means higher urgency. FreeRTOS uses these rules:

- Use one grouping with all bits as preemption priority (in HAL, `NVIC_PRIORITYGROUP_4`) and set it once at start-up.
- The kernel's own interrupts (PendSV, SysTick) run at the lowest priority.
- Interrupts that call `...FromISR` functions must have a priority number greater than or equal to the maximum syscall priority (less urgent or equal).
- Interrupts more urgent than that limit are never delayed by the kernel but must not call the API.

Typical configuration pattern with 4 bits:

```c
#ifdef __NVIC_PRIO_BITS
  #define configPRIO_BITS __NVIC_PRIO_BITS
#else
  #define configPRIO_BITS 4
#endif

#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY      15
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY  5

/* The port needs the values shifted into the implemented high bits. */
#define configKERNEL_INTERRUPT_PRIORITY \
    (configLIBRARY_LOWEST_INTERRUPT_PRIORITY << (8 - configPRIO_BITS))
#define configMAX_SYSCALL_INTERRUPT_PRIORITY \
    (configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY << (8 - configPRIO_BITS))
```

HAL functions such as `HAL_NVIC_SetPriority` take the unshifted number (0 to 15 here); the configuration macros above are shifted. Mixing the two scales is a common cause of the priority assert. Choose the syscall priority so that ISRs calling the API use numbers from that value up to 15, and time-critical ISRs use lower numbers.

Cortex-M0 and M0+ implement fewer priority bits (commonly 2), so the scheme must be adapted.

## Handler mapping

The kernel provides handlers for SVC, PendSV, and the tick. Map them to the vector table names, usually in the configuration header:

```c
#define vPortSVCHandler     SVC_Handler
#define xPortPendSVHandler  PendSV_Handler
/* The tick handler is mapped to SysTick_Handler, or called from it. */
```

If the HAL tick also uses SysTick, `SysTick_Handler` must call both the HAL tick increment and the kernel tick handler. The cleaner arrangement is below.

## HAL timebase

The HAL needs a time base for its timeouts. When FreeRTOS owns SysTick, move the HAL time base to a spare basic timer (the configuration tool offers this choice), and implement the timer's period callback to increment the HAL tick. The HAL timebase interrupt priority should not be lower than the interrupts of peripherals whose blocking HAL calls need it.

## Key configuration items

| Item | Notes |
|---|---|
| `configTICK_RATE_HZ` | 1000 is common; higher rates add overhead and shorten the longest delay |
| `configMAX_PRIORITIES` | Keep small; more costs RAM |
| `configMINIMAL_STACK_SIZE` | In words; used for the idle task |
| `configTOTAL_HEAP_SIZE` | Applies to heap schemes that use a static array |
| `configCHECK_FOR_STACK_OVERFLOW` | Use 2 during development and keep the hook active |
| `configUSE_MALLOC_FAILED_HOOK` | Catch allocation failure |
| `configASSERT` | Define it; route to a fault capture or breakpoint |
| `configSUPPORT_STATIC_ALLOCATION` | Allows creating kernel objects with static memory |
| `INCLUDE_uxTaskGetStackHighWaterMark` | Enables stack margin measurement |
| `configGENERATE_RUN_TIME_STATS` | Per-task CPU use; needs a time base faster than the tick |

## Heap schemes

The heap implementations differ: a simple one that never frees, one that frees without coalescing, one that coalesces adjacent free blocks (a common default), one that spans multiple RAM regions (useful when RAM is split into banks, such as main RAM and a second SRAM), and one that wraps the C library allocator. Prefer static allocation for long-running products; if dynamic allocation is used, size the heap from measured use and watch the minimum ever free size.

## Stack sizing and overflow

- The native task creation API takes the stack depth in words; the CMSIS-RTOS v2 wrapper takes bytes.
- Each task stack holds its call frames, the exception frame, and the saved context. Library calls such as formatted printing need large stacks.
- Overflow check method 2 fills the stack with a pattern and checks the last bytes at each switch; it can miss overflows that jump past the pattern, so keep margin and use the high-water mark.
- Interrupts use the main stack on Cortex-M ports; size it for the deepest interrupt nesting.

## Tickless idle

For low power, tickless idle stops the periodic tick when all tasks are blocked, enters a low-power mode, and restores the tick count on wake-up. On STM32 the default SysTick-based approach stops working in deep modes because the core timer stops; use a low-power timer or the RTC as the wake-up source in an application-provided implementation, and restore the clocks on wake. Verify with measurements and test timeouts and delays across sleeps.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| `configASSERT` in the interrupt priority check | ISR calling the API at too urgent a priority, priority scale mixed up, grouping not set | Check the priority number and scale of that interrupt, and the grouping |
| Hard fault at scheduler start | Wrong port, interrupts configured wrong, main stack too small | Compare port and core; check the handler mapping and stack |
| No task switches | PendSV or SysTick not mapped, tick handler not called | Check the vector names and the tick |
| Delays too long or short | Tick rate or the timebase confusion | Check tick frequency and the clock |
| Random corruption in a task | Stack overflow | Enable overflow detection, check the high-water mark |
| Heap allocation fails | Fragmentation or undersized heap | Check minimum free, switch to static objects |
| Low-priority task never runs | High-priority task never blocks | Review priorities, add blocking waits |
