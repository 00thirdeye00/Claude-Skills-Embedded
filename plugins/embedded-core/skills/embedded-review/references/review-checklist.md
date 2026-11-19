# Firmware review checklist

## Contents
- Correctness and robustness
- Concurrency and interrupts
- Memory and data
- Hardware interaction
- Timing and power
- Error handling and recovery
- Security
- Tooling and standards
- Testing

## Correctness and robustness
- Every function has defined behavior for invalid arguments, null pointers, zero lengths, and boundary values.
- Integer conversions, signed overflow, shifts by the type width, and division by zero are handled.
- Switch statements handle all cases and have a safe default.
- No reliance on undefined or implementation-defined behavior (strict aliasing, uninitialized reads, unaligned casts).
- State machines have explicit states, transitions, and handling for unexpected events.

## Concurrency and interrupts
- Each shared variable has one documented protection mechanism.
- ISRs are short, non-blocking, and clear their sources; no heap, no formatted I/O.
- Critical sections are short and restore the previous interrupt state.
- RTOS calls from ISRs use the ISR-safe variants and respect priority limits.
- Lock order is consistent; no blocking call while holding a lock unless intended.
- See `embedded-isr-concurrency` for detail.

## Memory and data
- Stack use is bounded; no large locals or recursion without analysis.
- No dynamic allocation after initialization, or allocation failure is handled.
- Buffers have size checks on every write; string functions are length-bounded.
- Structs written to wire or flash do not depend on padding or endianness unless packed and converted deliberately.
- DMA buffers are aligned, reachable by the DMA, and valid for the whole transfer; cache maintenance is correct on cached cores.
- Constants are `const` and live in flash; large tables are not copied to RAM by accident.

## Hardware interaction
- Register and shared flag accesses use `volatile`; read-modify-write of registers shared with ISRs is protected.
- Clocks, resets, and pin configuration are set before use, in the documented order.
- Every wait on hardware has a timeout and a failure path.
- Interrupt flags are cleared correctly; pending interrupts at start-up are handled.
- Magic numbers are replaced by named register fields or constants.
- Bus drivers recover from NACK, stuck lines, and aborted transfers.

## Timing and power
- Worst-case execution times and deadlines are stated and plausible.
- No busy-wait loops where sleeping or an event would do.
- Low-power transitions are guarded: peripherals quiesced, wake sources armed, state restored.
- Time arithmetic handles counter wrap-around.

## Error handling and recovery
- Return values are checked; errors propagate with context or are logged and counted.
- A watchdog is enabled and fed only when the system is healthy (not from an unconditional timer ISR).
- Fault handlers capture state and reset safely.
- Persistent data has integrity checks (CRC) and power-loss-safe update logic.

## Security
- Inputs from buses, radios, and files are validated for length and range.
- No secrets in source or logs; keys are stored in protected memory where available.
- Debug interfaces and bootloader modes are controlled according to the product's threat model.
- Firmware updates are authenticated and protected against rollback where required.

## Tooling and standards
- Builds clean with strict warnings, for example `-Wall -Wextra -Wconversion -Wshadow -Wformat=2`, and treat warnings as errors in CI.
- A static analyzer runs in CI (for example cppcheck or clang-tidy; add a MISRA checker when the standard applies). Deviations are documented.
- `-fstack-usage` output and the linker map are reviewed for RAM, stack, and flash growth.

## Testing
- Pure logic is unit-tested on the host.
- Drivers have a hardware-in-the-loop or loopback test, or a documented manual test.
- Failure paths (timeouts, bus errors, power loss) are exercised, not only the happy path.
