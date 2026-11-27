# Playbooks

Pick the closest one, then add, drop, or reorder stages for the goal. Stages marked (you) need the user's action or measurement before continuing.

## Contents
- Firmware for a given board
- Add a chip or peripheral to existing firmware
- Investigate a failure
- Add firmware updates
- Prepare a release

## Firmware for a given board

1. Collect inputs: part number, requirements, netlist or pin list, BOM, datasheets, toolchain, RTOS.
2. `stm32-pin-map` if a KiCad netlist exists: compact pin table. Checkpoint (you): confirm inferred signals.
3. `stm32-design`: pin, clock, DMA, memory, interrupt plan and module breakdown. Checkpoint (you): confirm alternate functions against the datasheet and approve the design.
4. `stm32-architecture` (create): modules, contracts, resource map, CLAUDE.md pointer. Checkpoint (you): approve the architecture before any code is written.
5. Hardware sanity (you): rails, boot pins, reset, debug header, oscillators measured before flashing.
6. `stm32-cubemx-config` (if CubeMX is used), `stm32-rtos` if an RTOS is used, and `stm32-linker-startup` for memory regions and startup. Checkpoint (you): project builds.
7. `stm32-peripherals` for first light: LED and UART log. Checkpoint (you): it runs on the board.
8. For each external chip: `stm32-driver-bringup`, with `stm32-peripherals` for its bus. Checkpoint (you): ID read and a known register verified on the bus. After each module, `stm32-architecture` (update).
9. `embedded-rtos-concepts` and `embedded-isr-concurrency` for task and data-flow design (if installed).
10. `stm32-testing`: host tests from the contracts and CI.
11. `stm32-power` if battery powered.
12. `stm32-bootloader-ota` if field updates are needed.
13. `stm32-security` if the threat model needs it.
14. `stm32-review` on the code.
15. `stm32-release`.

Generate code in the module layout from the architecture documents, and update the module contracts and the resource map in the same change.

## Add a chip or peripheral to existing firmware

If `docs/architecture/ARCHITECTURE.md` exists, use `stm32-extend`: it reads the index, the affected contracts, and dependency headers instead of the code base, and updates the documents. If it does not exist, run `stm32-architecture` (create) first.

1. `stm32-extend` for the change (it checks the resource map for conflicts).
2. `stm32-peripherals` for the bus or peripheral details, and `stm32-driver-bringup` for an external chip.
3. `stm32-testing` for the new module's tests.
4. `stm32-review` on the change.

## Investigate a failure

1. `stm32-debug` with the raw values or captures.
2. `stm32-peripherals` or `stm32-rtos` for the implicated area.
3. `embedded-debug` for instrumentation if the bug is intermittent (if installed).
4. `stm32-review` on the fix.

## Add firmware updates

1. `stm32-design` to confirm flash layout and erase granularity.
2. `stm32-bootloader-ota`.
3. `stm32-release` for protection settings and production flow.

## Prepare a release

1. `stm32-review` on the release candidate.
2. `stm32-release`.
3. `embedded-release` for generic items (if installed).
