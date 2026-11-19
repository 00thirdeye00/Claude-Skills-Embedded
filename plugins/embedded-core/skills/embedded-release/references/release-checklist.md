# Firmware release checklist

## Contents
- Build and traceability
- Memory and layout
- Image integrity and authenticity
- Runtime safety
- Bootloader and updates
- Protection and production
- Verification
- Documentation

## Build and traceability
- Toolchain version, SDK or HAL version, and build flags are pinned and recorded.
- The build is reproducible from a clean checkout; path-dependent strings are controlled (for example with a file-prefix mapping flag).
- Version number and commit hash are embedded in the image and readable at run time.
- ELF, map file, and build log are archived with the release.
- Release build has no debug-only code paths enabled by accident (assert behavior, verbose logging, test hooks).

## Memory and layout
- Flash and RAM headroom is recorded and above the project's margin.
- Stack and heap sizes are validated by measurement under worst-case load.
- Linker script regions match the hardware (flash size, RAM banks, bootloader and slot offsets).
- Vector table location is correct for the image (including when started by a bootloader).

## Image integrity and authenticity
- Image has an integrity check (CRC or hash) verified before running.
- Where required, images are signed and the bootloader verifies the signature; keys are managed outside the repository.
- Version policy prevents installing unintended downgrades.

## Runtime safety
- Watchdog is enabled in the release configuration and fed only from a health-checked point.
- Brown-out detection level suits the supply and flash-write needs.
- Fault handlers record state and reset safely; behavior after repeated resets is defined (safe mode).
- Non-volatile data has versioning, integrity checks, and migration from older layouts.

## Bootloader and updates
- Power loss during an update, at every stage, leaves a bootable device.
- A failed or incompatible image rolls back or stays in the bootloader.
- Update works from the previous released versions, including the oldest supported one.
- Interrupted transfers, corrupted images, and wrong-device images are rejected.
- Bootloader itself is protected from accidental overwrite.

## Protection and production
- Debug access and read-out protection settings follow the product policy and have been tested on a production-programmed unit.
- Irreversible protection settings are applied only on an explicit decision.
- Production programming procedure is documented, repeatable, and writes unique data (serial number, calibration, keys) safely.
- Manufacturing test covers the peripherals and calibrations the product depends on.

## Verification
- Full regression passes on the exact release binary, on the supported hardware revisions.
- Temperature, supply-variation, and long-run tests are done to the product's requirements.
- Known issues are listed with workarounds and severity.

## Documentation
- Release notes list changes, known issues, upgrade steps, and rollback steps.
- Support and field-service teams have the version identification method and recovery procedure.
