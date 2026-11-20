# STM32 families: core, fault model, and debug differences

Use this map to decide which fault registers exist, whether an FPU or cache is involved, and which pitfalls to check first. Family-to-core assignments are stable but new families keep appearing: for a part not listed, read the core from the datasheet ("Arm Cortex-M..." on the first page) and apply the matching row.

## Contents
- Family map
- What the core implies
- Dual-core parts
- Family quirks worth checking first

## Family map

| Family (examples) | Core | FPU | Fault registers | Cache / TCM |
|---|---|---|---|---|
| F0, G0, L0, C0 | Cortex-M0 or M0+ | No | HardFault only | No |
| F1, F2, L1 | Cortex-M3 | No | CFSR, HFSR, MMFAR, BFAR | No |
| F3, F4, G4, L4, L4+ | Cortex-M4 | Single precision (M4F) | CFSR, HFSR, MMFAR, BFAR | F4: ART accelerator (instruction/data prefetch), not a CPU cache |
| F7, H7 | Cortex-M7 | Single or double precision | CFSR, HFSR, MMFAR, BFAR | L1 I-cache and D-cache; TCM RAM |
| L5, U5, H5, WBA | Cortex-M33 | Yes (family dependent) | CFSR plus STKOF, secure fault registers with TrustZone | Family dependent |
| WB, WL | Cortex-M4 plus a Cortex-M0+ radio core | M4: yes | M4 as above | No |
| H745, H747, H755, H757 | Cortex-M7 plus Cortex-M4 | Both | Both cores as above | M7 only |

Confirm the core, FPU, MPU, and cache for the exact part in its datasheet and reference manual. Optional features (MPU, FPU precision, TrustZone) vary inside a family.

## What the core implies

- **M0 / M0+:** No CFSR. Unaligned accesses cause a HardFault. Use the Thumb-1 handler from `hardfault-decode.md`. Many `UsageFault` causes seen on bigger cores (undefined instruction, bad state) all arrive as HardFault, so rely on the stacked PC and the disassembly.
- **M3 / M4:** Full fault status. M4F needs the FPU enabled (`CPACR`) before the first floating-point instruction; a hard-float build with a custom startup that skips `SystemInit()` gives `NOCP`.
- **M7:** Adds caches and TCM. Suspect cache coherency whenever DMA, Ethernet, SDMMC, or another bus master shares memory with the CPU. Check which RAM the DMA can reach. Imprecise bus faults are common because of deeper write buffering.
- **M33:** Adds `STKOF` and stack-limit registers (`MSPLIM`, `PSPLIM`), and with TrustZone, secure and non-secure states with separate stacks and `EXC_RETURN` encodings. Debug each state's fault registers separately and use the Arm ARMv8-M reference for exception return details.

## Dual-core parts

- Debug each core as its own target and confirm which core owns each peripheral and memory region. Boot order, shared RAM, and hardware semaphores (HSEM) are frequent sources of "works on one core only" bugs.
- On the wireless families (WB, WL, WBA) the radio stack runs on a separate core with its own firmware. Faults there may not be visible from the application core. Check the vendor's wireless stack release notes for supported combinations.

## Family quirks worth checking first

| Family group | Check first |
|---|---|
| F0, G0 | Aligned access only; flash wait states when raising clock; startup file and vector table remap (some parts remap SRAM or flash to address 0) |
| F1 | AFIO remap and JTAG/SWD pin release; older HAL I2C reliability, and the I2C errata notes |
| F4 | CCM RAM not reachable by DMA; DMA stream/channel table; overdrive and voltage scale for the top frequency; RTC and backup domain access |
| F7, H7 | D-cache and DMA coherency; DMA-reachable RAM selection; MPU region setup for non-cacheable buffers; regulator and supply configuration before raising clocks |
| G4, L4 | Kernel clock mux selection (RCC CCIPR); DMAMUX request IDs; low-power modes and debug-in-low-power bits |
| L0, L4, U5 | Low-power behavior: peripherals and clocks that stop in Stop modes; wake-up clock; debug connection loss in low power |
| U5, L5, H5 | TrustZone: secure/non-secure option bytes, peripheral security attributes, and which world the code runs in |
| WB, WL | Radio core firmware version compatibility; shared resources with the radio core |

Verify each item against the reference manual, datasheet, and errata sheet for the exact part and silicon revision, because family documents change between revisions.
