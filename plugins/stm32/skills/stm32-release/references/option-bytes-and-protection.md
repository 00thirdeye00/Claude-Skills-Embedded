# Option bytes and protection

Option-byte names, encodings, and behavior differ by family. Use the reference manual's option-byte and protection sections for the exact part. The notes below describe common concepts.

## Contents
- Read-out protection
- Write protection
- Brown-out reset level
- Watchdog configuration
- Boot configuration
- CRC and version data
- Production programming and verification

## Read-out protection

| Level | Typical behavior |
|---|---|
| Level 0 | No protection; debugger can read flash and RAM |
| Level 1 | Flash read-out protection; debug access cannot read flash; moving back to level 0 triggers a mass erase of user flash |
| Level 2 | Permanent; debug access disabled; the change cannot be undone |

Details vary by family. Newer security-oriented families add intermediate levels and security-domain settings. A device at the highest level cannot be debugged or re-flashed through the debug port, and the system bootloader may be disabled, so a bug in the update path then makes the device unrecoverable. Treat that level as a final production decision that requires explicit sign-off.

Level 1 can complicate field returns and debugging; some products accept that and others require the highest level against cloning. Decide from the threat model.

## Write protection

Write protection marks flash sectors or pages as protected against erase and programming, which can protect the bootloader from accidental overwrite. Check how it interacts with your update scheme: protected regions cannot be updated until the protection is lifted.

## Brown-out reset level

A brown-out reset holds the device in reset when the supply drops below the selected threshold. Choose the threshold from the supply range, the minimum voltage for flash programming and the external devices, and battery behavior. A too-high threshold prevents operation near the end of the battery's life; a too-low one allows erratic behavior during supply sag.

## Watchdog configuration

The independent watchdog can be started by software or forced on by an option bit at reset (hardware mode). Hardware mode protects against firmware that never starts the watchdog. Decide the timeout from the worst-case loop or task time plus margin, and feed it only after health checks pass. Check how the watchdog behaves in stop and standby modes and while the debugger halts the core.

## Boot configuration

Option bits (and on some families boot pins) choose the start-up location: user flash, system memory, or embedded SRAM. In production, make sure the boot configuration matches the plan for the bootloader, and that floating boot pins cannot change it.

## CRC and version data

- Store a version and a CRC of the image in a known location, and have the application or bootloader verify it.
- The device has a unique ID and flash-size registers at part-specific addresses; use them for serial numbers or key derivation only after confirming their meaning in the reference manual.

## Production programming and verification

1. Program the image (and bootloader) with the vendor's command-line programmer or a production tool; script the steps.
2. Write per-unit data (serial number, calibration) to its reserved area in a way that survives updates.
3. Program option bytes as the last step, then read them back and compare against the expected values.
4. Verify the flash contents by read-back or CRC where read protection allows it, before enabling the protection.
5. Run a functional test, then confirm that the debug-access behavior matches the policy.
6. Keep a record per unit (version, serial number, test result).
