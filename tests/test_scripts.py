"""Tests for the helper scripts, using small synthetic fixtures.

Run from the repository root:  python3 -m unittest discover -s tests -v

The fixtures imitate the documented formats (KiCad s-expression netlist, GNU ld map,
GCC .su files). They are not output captured from real tools, so also try the scripts
on your own files.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "plugins", "stm32", "skills")
FX = os.path.join(ROOT, "tests", "fixtures")


def run(script, *args, cwd=None):
    p = subprocess.run([sys.executable, os.path.join(SK, script), *args], capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


class DecodeFault(unittest.TestCase):
    S = "stm32-debug/scripts/decode_fault.py"

    def test_precise_bus_error(self):
        rc, out = run(self.S, "--cfsr", "0x00008200", "--bfar", "0x40021000", "--pc", "0x08001a45")
        self.assertEqual(rc, 0)
        self.assertIn("PRECISERR", out)
        self.assertIn("BFARVALID", out)
        self.assertIn("Peripherals", out)
        self.assertIn("addr2line", out)

    def test_usage_fault_bits(self):
        rc, out = run(self.S, "--cfsr", "0x03000000")
        self.assertIn("UNALIGNED", out)
        self.assertIn("DIVBYZERO", out)

    def test_forced_hardfault(self):
        rc, out = run(self.S, "--hfsr", "0x40000000", "--cfsr", "0x00020000")
        self.assertIn("FORCED", out)
        self.assertIn("INVSTATE", out)

    def test_m0_note(self):
        rc, out = run(self.S, "--core", "m0", "--pc", "0x08000100")
        self.assertIn("no CFSR", out)


class NetlistPins(unittest.TestCase):
    S = "stm32-pin-map/scripts/netlist_pins.py"

    def test_table(self):
        rc, out = run(self.S, os.path.join(FX, "board.net"), "--format", "csv")
        self.assertEqual(rc, 0, out)
        lines = out.splitlines()
        self.assertTrue(lines[0].startswith("# U1"))
        self.assertIn("6 pins, 3 GPIO, 1 not connected", lines[0])
        rows = [l for l in lines if "," in l and not l.startswith("#")]
        funcs = [r.split(",")[1] for r in rows[1:]]
        self.assertEqual(funcs[:3], ["PA3", "PA12", "PB8"])
        pb8 = next(r for r in rows if ",PB8," in r)
        self.assertIn("/I2C1_SCL", pb8)
        self.assertIn("U2.13(SCL)", pb8)
        self.assertIn("R1.1", pb8)
        pa3 = next(r for r in rows if ",PA3," in r)
        self.assertIn(",NC,", pa3)
        pa12 = next(r for r in rows if ",PA12," in r)
        self.assertIn("single node", pa12)
        self.assertEqual(funcs[-1], "VSS")

    def test_names_from_libparts(self):
        rc, out = run(self.S, os.path.join(FX, "board_nofunc.net"))
        self.assertEqual(rc, 0, out)
        self.assertIn("| PB8 |", out)
        self.assertIn("| NRST |", out)

    def test_list_and_bad_ref(self):
        rc, out = run(self.S, os.path.join(FX, "board.net"), "--list")
        self.assertIn("U1\tSTM32G474RETx", out)
        rc, out = run(self.S, os.path.join(FX, "board.net"), "--ref", "U9")
        self.assertNotEqual(rc, 0)

    def test_not_a_netlist(self):
        rc, out = run(self.S, os.path.join(FX, "firmware.map"))
        self.assertNotEqual(rc, 0)


class MapAndStack(unittest.TestCase):
    def test_map_summary(self):
        rc, out = run("stm32-linker-startup/scripts/map_summary.py", os.path.join(FX, "firmware.map"))
        self.assertEqual(rc, 0, out)
        flash = next(l for l in out.splitlines() if l.startswith("| FLASH"))
        ram = next(l for l in out.splitlines() if l.startswith("| RAM"))
        self.assertIn("| 4520 |", flash)   # 0x188 + 0x1000 + 0x20 (.data load address)
        self.assertIn("| 3616 |", ram)     # 0x20 + 0x800 + 0x600
        self.assertIn("build/stm32f4xx_hal.o", out)
        self.assertIn("._user_heap_stack", out)

    def test_stack_usage(self):
        rc, out = run("stm32-linker-startup/scripts/stack_usage.py", os.path.join(FX, "build"), "--warn", "200")
        self.assertEqual(rc, 0, out)
        self.assertIn("| 256 | dynamic,bounded | uart_send", out)
        self.assertIn("LARGE", out)
        rc, out = run("stm32-linker-startup/scripts/stack_usage.py", os.path.join(FX, "sample_fw"))
        self.assertNotEqual(rc, 0)


class ArchitectureCheck(unittest.TestCase):
    S = "stm32-architecture/scripts/check_architecture.py"

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.fw = os.path.join(self.tmp, "fw")
        shutil.copytree(os.path.join(FX, "sample_fw"), self.fw)
        self.arch = os.path.join(self.fw, "docs", "architecture", "ARCHITECTURE.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def check(self):
        return run(self.S, "--arch", self.arch, "--root", self.fw, "--src", "src", "Core")

    def edit(self, path, old, new):
        with open(path) as f:
            t = f.read()
        self.assertIn(old, t)
        with open(path, "w") as f:
            f.write(t.replace(old, new))

    def test_clean(self):
        rc, out = self.check()
        self.assertEqual(rc, 0, out)
        self.assertIn("0 errors", out)

    def test_upward_dependency(self):
        self.edit(self.arch, "| bsp | BSP | Clocks, pins, HAL port | src/bsp/bsp.h | none |", "| bsp | BSP | Clocks, pins, HAL port | src/bsp/bsp.h | app |")
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("depends upward", out)
        self.assertIn("cycle", out)

    def test_undeclared_include(self):
        self.edit(os.path.join(self.fw, "src/drivers/imu/imu.c"), '#include "bsp.h"', '#include "bsp.h"\n#include "can_comm.h"')
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("not a declared dependency", out)

    def test_irq_priority_drift(self):
        self.edit(os.path.join(self.fw, "Core/main.c"), "FDCAN1_IT0_IRQn, 5", "FDCAN1_IT0_IRQn, 3")
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("table priority 5 but code sets [3]", out)

    def test_duplicate_pin_and_unknown_owner(self):
        self.edit(self.arch, "| PA12 | FDCAN1_TX | AF9 | can_comm | |", "| PB8 | FDCAN1_TX | AF9 | ghost | |")
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("listed twice", out)
        self.assertIn("owner 'ghost'", out)

    def test_missing_contract(self):
        os.remove(os.path.join(self.fw, "docs/architecture/modules/imu.md"))
        rc, out = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("no contract", out)


if __name__ == "__main__":
    unittest.main()
