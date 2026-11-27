#!/usr/bin/env python3
"""Decode Cortex-M (ARMv7-M / ARMv8-M Mainline) fault registers.

Usage:
  decode_fault.py --cfsr 0x00008200 [--hfsr 0x40000000] [--bfar 0x40021000]
                  [--mmfar 0x0] [--pc 0x08001a44] [--lr 0x08001a21]

Core-level facts only (Arm architecture). Cortex-M0/M0+ cores have no CFSR.
Addresses are classified with the standard Arm memory map; confirm part-specific
ranges in the reference manual.
"""
import argparse
import sys

MMFSR = {0: ("IACCVIOL", "Instruction fetch violated MPU or execute-never rules"),
         1: ("DACCVIOL", "Data access violated MPU rules"),
         3: ("MUNSTKERR", "MPU fault while unstacking on exception return"),
         4: ("MSTKERR", "MPU fault while stacking on exception entry"),
         5: ("MLSPERR", "MPU fault during lazy FP state save"),
         7: ("MMARVALID", "MMFAR holds the faulting address")}
BFSR = {8: ("IBUSERR", "Bus error on instruction fetch"),
        9: ("PRECISERR", "Precise data bus error; stacked PC is the faulting instruction"),
        10: ("IMPRECISERR", "Imprecise data bus error; stacked PC may be later than the cause"),
        11: ("UNSTKERR", "Bus error while unstacking"),
        12: ("STKERR", "Bus error while stacking"),
        13: ("LSPERR", "Bus error during lazy FP state save"),
        15: ("BFARVALID", "BFAR holds the faulting address")}
UFSR = {16: ("UNDEFINSTR", "Undefined instruction executed"),
        17: ("INVSTATE", "Invalid EPSR state, usually Thumb bit clear"),
        18: ("INVPC", "Invalid exception return value"),
        19: ("NOCP", "Coprocessor instruction with the coprocessor disabled (FPU not enabled?)"),
        20: ("STKOF", "Stack overflow detected by stack limit (ARMv8-M only)"),
        24: ("UNALIGNED", "Unaligned access trapped"),
        25: ("DIVBYZERO", "Divide by zero trapped")}
HFSR = {1: ("VECTTBL", "Bus fault reading the vector table (bad VTOR?)"),
        30: ("FORCED", "A configurable fault escalated; read CFSR"),
        31: ("DEBUGEVT", "Debug event while debug is disabled")}
HINTS = {
    "IACCVIOL": "Jumped to a non-executable region or bad function pointer; check the stacked PC.",
    "DACCVIOL": "MPU guard hit (stack or NULL guard) or wild pointer; read MMFAR if valid.",
    "MSTKERR": "Stack overflow into a protected region; check stack sizes.",
    "MUNSTKERR": "Stack corrupted inside the ISR; check the stack pointer.",
    "IBUSERR": "Branch to an unmapped or unpowered address.",
    "PRECISERR": "Inspect BFAR against the memory map; for peripherals check the RCC clock enable first.",
    "IMPRECISERR": "Cause may be a few instructions earlier; on Cortex-M3/M4 set ACTLR.DISDEFWBUF to make it precise while debugging.",
    "STKERR": "Stack pointer outside valid memory; suspect stack overflow.",
    "UNSTKERR": "Corrupted or invalid stack pointer on return.",
    "UNDEFINSTR": "Executing data or erased flash, or wrong -mcpu/-mfpu build flags.",
    "INVSTATE": "Function pointer or return address with bit 0 clear; check vector table entries and pointers.",
    "INVPC": "Corrupted stack or EXC_RETURN inside an ISR.",
    "NOCP": "Enable the FPU (SCB->CPACR) in startup before the first FP instruction.",
    "UNALIGNED": "Unaligned LDM/STM/LDRD, or CCR.UNALIGN_TRP is set.",
    "DIVBYZERO": "CCR.DIV_0_TRP is set and a divisor was zero.",
    "VECTTBL": "Vector table unreadable: check SCB->VTOR and the application link address.",
    "FORCED": "Decode CFSR for the real cause.",
    "STKOF": "Increase the stack size or find the deep call chain.",
}

REGIONS = [(0x00000000, 0x1FFFFFFF, "Code (flash, boot alias, system memory, some TCM/CCM)"),
           (0x20000000, 0x3FFFFFFF, "SRAM"),
           (0x40000000, 0x5FFFFFFF, "Peripherals (check RCC clock enable for the peripheral)"),
           (0x60000000, 0x9FFFFFFF, "External memory (FMC/FSMC/OctoSPI)"),
           (0xA0000000, 0xDFFFFFFF, "External device / reserved"),
           (0xE0000000, 0xE00FFFFF, "Private peripheral bus (SCB, NVIC, SysTick, debug)")]


def classify(addr):
    for lo, hi, name in REGIONS:
        if lo <= addr <= hi:
            return name
    return "System / vendor-specific"


def flags(value, table):
    return [(bit, *table[bit]) for bit in sorted(table) if value >> bit & 1]


def num(s):
    return int(s, 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cfsr", type=num)
    ap.add_argument("--hfsr", type=num)
    ap.add_argument("--mmfar", type=num)
    ap.add_argument("--bfar", type=num)
    ap.add_argument("--pc", type=num)
    ap.add_argument("--lr", type=num)
    ap.add_argument("--core", default="m4", help="m0 prints the no-CFSR note (m0, m0+, m3, m4, m7, m33)")
    a = ap.parse_args(argv)
    out = []
    if a.core.lower() in ("m0", "m0+", "m0plus"):
        out.append("Cortex-M0/M0+ has only HardFault and no CFSR/HFSR/MMFAR/BFAR. Use the stacked PC and LR with addr2line and objdump.")
    if a.hfsr is not None:
        out.append(f"HFSR = 0x{a.hfsr:08X}")
        for bit, name, desc in flags(a.hfsr, HFSR):
            out.append(f"  bit {bit:2d} {name}: {desc}")
    if a.cfsr is not None:
        mm, bf, uf = a.cfsr & 0xFF, (a.cfsr >> 8) & 0xFF, (a.cfsr >> 16) & 0xFFFF
        out.append(f"CFSR = 0x{a.cfsr:08X}  (MMFSR=0x{mm:02X}, BFSR=0x{bf:02X}, UFSR=0x{uf:04X})")
        found = []
        for title, table, val in (("MemManage", MMFSR, a.cfsr), ("BusFault", BFSR, a.cfsr), ("UsageFault", UFSR, a.cfsr)):
            fl = flags(val, table)
            for bit, name, desc in fl:
                out.append(f"  {title:10s} bit {bit:2d} {name}: {desc}")
                found.append(name)
        if not found:
            out.append("  No known fault bits set.")
        valid = {"MMARVALID": a.mmfar, "BFARVALID": a.bfar}
        for name, addr in valid.items():
            if name in found and addr is None:
                out.append(f"  Note: {name} is set; pass the matching address register.")
        hints = [f"  {n}: {HINTS[n]}" for n in found if n in HINTS]
        if hints:
            out.append("Hints:")
            out.extend(hints)
    if a.hfsr is not None:
        for bit, name, desc in flags(a.hfsr, HFSR):
            if name in HINTS:
                out.append(f"  {name}: {HINTS[name]}")
    for label, val, flagname in (("MMFAR", a.mmfar, "MMARVALID"), ("BFAR", a.bfar, "BFARVALID")):
        if val is not None:
            ok = a.cfsr is None or any(n == flagname for _, n, _ in flags(a.cfsr, {**MMFSR, **BFSR}))
            tag = "" if ok else "  (ignore: valid bit not set in CFSR)"
            out.append(f"{label} = 0x{val:08X}: {classify(val)}{tag}")
    for label, val in (("PC", a.pc), ("LR", a.lr)):
        if val is not None:
            thumb = "Thumb bit set" if val & 1 else "Thumb bit CLEAR (suspicious for a return address)"
            out.append(f"{label} = 0x{val:08X}: {classify(val)}; {thumb}")
            out.append(f"  arm-none-eabi-addr2line -e <elf> -f -p -i 0x{val & ~1:08X}")
    if len(out) == 0:
        out.append("Nothing to decode: pass at least --cfsr or --hfsr.")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
