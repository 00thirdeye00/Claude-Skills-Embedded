# Linker scripts and startup for STM32

Example values are for a part with 512 KB flash at 0x08000000 and 96 KB RAM at 0x20000000. Replace every address and size from the reference manual of your part.

## Contents
- Linker script structure
- Special sections
- Vector table placement and alignment
- Startup sequence
- Bootloader and slot offsets
- Checking a build

## Linker script structure

```ld
ENTRY(Reset_Handler)
_estack = ORIGIN(RAM) + LENGTH(RAM);
_Min_Heap_Size  = 0x200;
_Min_Stack_Size = 0x400;

MEMORY
{
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
  RAM   (xrw) : ORIGIN = 0x20000000, LENGTH = 96K
}

SECTIONS
{
  .isr_vector : { . = ALIGN(4); KEEP(*(.isr_vector)) . = ALIGN(4); } >FLASH
  .text : { . = ALIGN(4); *(.text) *(.text*) KEEP(*(.init)) KEEP(*(.fini)) . = ALIGN(4); } >FLASH
  .rodata : { . = ALIGN(4); *(.rodata) *(.rodata*) . = ALIGN(4); } >FLASH
  .ARM.extab : { *(.ARM.extab* .gnu.linkonce.armextab.*) } >FLASH
  .ARM : { __exidx_start = .; *(.ARM.exidx*) __exidx_end = .; } >FLASH

  _sidata = LOADADDR(.data);
  .data : { . = ALIGN(4); _sdata = .; *(.data) *(.data*) . = ALIGN(4); _edata = .; } >RAM AT> FLASH
  .bss  : { . = ALIGN(4); _sbss = .; *(.bss) *(.bss*) *(COMMON) . = ALIGN(4); _ebss = .; } >RAM

  ._user_heap_stack : { . = ALIGN(8); PROVIDE(end = .); PROVIDE(_end = .);
                        . = . + _Min_Heap_Size; . = . + _Min_Stack_Size; . = ALIGN(8); } >RAM
  .ARM.attributes 0 : { *(.ARM.attributes) }
}
```

Points to keep: `.data` runs in RAM but is stored in flash (`AT> FLASH`), the startup copies it using `_sidata`, `_sdata`, `_edata`; `.bss` is zeroed from `_sbss` to `_ebss`; the final section reserves a minimum heap and stack so the linker errors if RAM runs out.

## Special sections

- **DMA buffers** in a specific RAM (or a non-cacheable one): add a memory region and a section.

```ld
  .dma_buffers (NOLOAD) : { . = ALIGN(32); *(.dma_buffers) . = ALIGN(32); } >RAM_DMA
```

```c
__attribute__((section(".dma_buffers"), aligned(32))) static uint8_t rx_buf[256];
```

Use `NOLOAD` for uninitialized data. Initialized data in a non-main RAM needs its own load address and startup copy loop. Align cache-line sized for cached cores.

- **Retained data** across resets (backup SRAM or a no-init area): a `NOLOAD` section that startup does not clear.
- **Code in RAM** (flash programming routines, time-critical code): a section with `>RAM AT> FLASH` and a startup copy, or a `ramfunc` attribute provided by your toolchain.
- **External memory:** regions for external flash or RAM, available only after the interface is initialized; initialize it before copying data that lives there.
- **Stack guard:** leave a gap or an MPU region at the stack limit so overflow faults rather than corrupts.

## Vector table placement and alignment

The vector table must be aligned to a power of two at least as large as the table (and not less than 128 bytes). The table size is 4 bytes times the number of exceptions and interrupts plus the core's 16 entries. When the application starts at an offset (after a bootloader), the offset must satisfy this alignment, and the application sets `SCB->VTOR` to its table. Check the requirement for your part in the Arm architecture documentation and the reference manual; offsets like 0x200 are often too small for parts with many interrupts.

## Startup sequence

```c
extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss;
extern void SystemInit(void);
extern void __libc_init_array(void);
extern int main(void);

void Reset_Handler(void)
{
    uint32_t *src = &_sidata, *dst = &_sdata;
    while (dst < &_edata) { *dst++ = *src++; }          /* copy initialized data */
    for (dst = &_sbss; dst < &_ebss; ) { *dst++ = 0; }  /* clear bss */
    SystemInit();                                       /* clock defaults, FPU enable, VTOR */
    __libc_init_array();                                /* static constructors */
    (void)main();
    for (;;) { }
}
```

The first vector table entry is the initial stack pointer (`_estack`), the second is `Reset_Handler`. Interrupt handlers not defined by the application should resolve to a default handler (a weak alias) that loops or records the fault. Install a fault handler that captures state (see the debug skill). On cores with an FPU, enable the coprocessor before any floating-point code runs. If a data cache or tightly coupled memory is used, set it up before it matters.

## Bootloader and slot offsets

- Place the application at its slot address by setting `FLASH ORIGIN` and `LENGTH` to the slot, and the vector table at the slot start.
- Keep the application's `VTOR` offset consistent with the link address; mismatches fault immediately after the jump.
- Reserve a header or trailer area if the bootloader needs one (image headers, signatures), and leave the first bytes as the bootloader format requires.

## Checking a build

```
arm-none-eabi-size firmware.elf
arm-none-eabi-objdump -h firmware.elf        # section addresses and load addresses
arm-none-eabi-nm --size-sort -S firmware.elf | tail -20
python scripts/map_summary.py firmware.map
python scripts/stack_usage.py build/
```

Check: the vector table is at the slot start, `.data` has a load address in flash, region usage leaves margin, no section lands in an unexpected region, large frames are justified, and `_estack` equals the top of the stack region.
