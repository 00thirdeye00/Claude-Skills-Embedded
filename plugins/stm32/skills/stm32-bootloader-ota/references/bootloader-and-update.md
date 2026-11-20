# STM32 bootloaders and updates

Addresses, option bits, sector sizes, and protocols depend on the part. Confirm them in the reference manual and in the application note on STM32 system memory boot mode (AN2606), which lists boot entry and interfaces for each device. Related application notes describe the USART bootloader protocol (AN3155) and the USB DFU protocol (AN3156).

## Contents
- Choosing an approach
- Built-in system bootloader
- Flash layout and erase granularity
- Custom bootloader handover
- Application side
- Image integrity
- A/B slots and rollback
- MCUboot
- Failure modes

## Choosing an approach

| Approach | Good for | Limits |
|---|---|---|
| Built-in system bootloader | Factory programming, simple field updates over UART, USB DFU, I2C, SPI, or CAN depending on the part | No custom authentication or rollback; the interfaces are fixed by the part |
| Custom bootloader | Custom transports, simple validation, special behavior | You own all safety and security logic |
| MCUboot | Signed images, swap, confirm and rollback, wide platform support, native Zephyr integration | Configuration effort; flash and slot overhead; check sector-layout constraints |

## Built-in system bootloader

- It lives in ROM in system memory and is entered at reset through a boot pin or option bytes (the method depends on the family), or by software: deinitialize peripherals and interrupts, load the stack pointer from the first word of the system memory, and jump to the reset vector stored at the next word. Some families also need the system memory mapped at address zero before the jump. The system memory base address and the procedure are in AN2606.
- Host tools such as the vendor's programmer utility or an open-source DFU tool talk to it.
- Read-out protection restricts what the bootloader can read or write.

## Flash layout and erase granularity

- Flash must be erased before it is written. The erase unit is a page on many families and a sector on others, and some families have non-uniform sector sizes (small sectors first, then larger ones). Place slot boundaries on erase boundaries.
- The programming unit (for example word, double word, or a wider flash word) sets the alignment of writes.
- On a single-bank device, code fetches from flash stall during erase and programming. Run time-critical code from RAM or use the second bank of a dual-bank device while updating the other bank.
- Reserve a small configuration area (version, flags, counters) in its own erase unit.

Typical layout: `[bootloader][slot A (active)][slot B (update)][config]`. Keep the bootloader area small and protect it from accidental writes.

## Custom bootloader handover

```c
typedef void (*app_entry_t)(void);

void jump_to_app(uint32_t app_base)
{
    uint32_t msp   = *(volatile uint32_t *)app_base;          /* initial stack pointer */
    uint32_t reset = *(volatile uint32_t *)(app_base + 4u);   /* reset handler address */

    /* Basic sanity: msp inside RAM, reset inside the app slot (use the part's real limits). */

    __disable_irq();
    SysTick->CTRL = 0u; SysTick->LOAD = 0u; SysTick->VAL = 0u;
    for (uint32_t i = 0; i < (sizeof(NVIC->ICER) / sizeof(NVIC->ICER[0])); i++) {
        NVIC->ICER[i] = 0xFFFFFFFFu;                          /* disable all interrupts */
        NVIC->ICPR[i] = 0xFFFFFFFFu;                          /* clear pending */
    }
    /* Deinitialize peripherals and clocks the bootloader used (HAL deinit calls). */

    SCB->VTOR = app_base;
    __DSB(); __ISB();
    __set_MSP(msp);
    ((app_entry_t)reset)();
}
```

Cortex-M0 and M0+ cores may not have `SCB->VTOR` (some implement it, some remap the vector table in a system register); follow the reference manual for the part.

## Application side

- Link the application at its slot address: set the flash origin in the linker script and the vector table offset so startup code sets `SCB->VTOR` correctly (CMSIS system files expose a vector table offset setting).
- Re-enable interrupts and start the tick after the application initializes its own clocks.
- If an RTOS is used, its start-up must not assume the bootloader's interrupt state.

## Image integrity

- Add a header (magic, version, length, hardware ID) and a trailer or header field with a CRC or hash. Verify before jumping.
- If using the hardware CRC unit, check its polynomial, initial value, input and output reflection, and word-wise processing, which differ from common software CRC-32 routines. Ensure the host-side tool computes the same value.
- For authenticity use a digital signature verified with a public key stored in the bootloader; keep private keys off the device and out of the repository.

## A/B slots and rollback

1. Receive the new image into the inactive slot, verify integrity.
2. Mark the inactive slot as pending in a small, power-loss-safe flag area (write a new record instead of rewriting in place).
3. Reboot into the new image in a trial state.
4. The new application runs self-checks and confirms the image; if it never confirms (watchdog reset or timeout), the bootloader reverts.
5. Count boot attempts and enforce a limit.

## MCUboot

MCUboot is an open-source secure bootloader. Images have a header and a signature trailer, and a signing tool produces them. Typical elements:

- Two slots (primary and secondary), with modes such as swap, overwrite-only, direct execute-in-place, or RAM load. Swap modes need a scratch area or a move area and a status trailer.
- Test and confirm flow: a new image runs once on trial and reverts unless it is confirmed.
- Signing keys (for example ECDSA or Ed25519) and an image tool (`imgtool`) to sign images with the header size, alignment, version, and slot size matching the bootloader configuration. Run `imgtool sign --help` for the options of your version.
- Zephyr builds integrate MCUboot as a build component and sign images as part of the build; other RTOSes use the bootloader as a separate project.
- Slot sizes must match flash erase boundaries; on parts with non-uniform sectors, check the swap algorithm's requirements and choose a mode and slot layout that fit.

## Failure modes

| Symptom | Likely cause | Check |
|---|---|---|
| App hard-faults right after the jump | Vector table offset not set, wrong link address, interrupts left enabled, peripherals in a state the app does not expect | Compare `VTOR`, the initial stack pointer, and the reset vector with the map file |
| App runs only under the debugger | Different boot state, clocks, or interrupt state | Reset-and-run test through the bootloader path |
| Flash write fails or corrupts | Not erased, wrong alignment, flash locked, voltage range, interrupts stalled | Check status flags and the erase, unlock, and program sequence |
| Update bricks after power loss | Commit not atomic, slot overwritten in place | Redesign with staging and a flag record; test power loss at every step |
| CRC mismatch on a good image | Host and device CRC parameters differ | Compare polynomial, initial value, reflection, and word order |
| System bootloader entry fails | Boot pins or option bits wrong, read-out protection | Check boot configuration and protection level |
