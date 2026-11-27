# STM32 security notes

All details vary by family and silicon revision. Treat this as a map of topics; confirm every mechanism and configuration in the reference manual and the security application notes for the part.

## Contents
- Controls overview
- Debug and read-out protection
- Secure boot and updates
- TrustZone on Cortex-M33 parts
- Keys and crypto hardware
- Production and lifecycle
- Verification

## Controls overview

| Goal | Typical controls |
|---|---|
| Protect firmware from readout | Read-out protection level, debug lock, disabling system bootloader or restricting it, encrypted images |
| Ensure only authentic firmware runs | Secure boot with signature verification of the next stage, immutable first stage |
| Prevent downgrade | Version counters in protected storage, bootloader enforcing version policy |
| Protect keys | Secure storage areas, OTP, hardware key features where the part has them, never in plain flash |
| Isolate critical code | Memory protection unit, TrustZone secure and non-secure worlds |
| Protect communication | Authenticated and encrypted channels using standard protocols and libraries |

## Debug and read-out protection

Read-out protection restricts debug and flash readout; the highest level is permanent and also limits what a legitimate recovery can do. Newer families add debug authentication and intermediate levels. Decide the policy per lifecycle stage, test regression behavior on spare units, and make sure the update path still works at the chosen level.

## Secure boot and updates

- A first-stage bootloader that cannot be modified in the field verifies the signature (and version) of the next stage before running it.
- Keep private keys offline; embed only public keys or hashes. Plan key rotation and revocation.
- Updates are authenticated before installation and installed atomically with rollback to a known-good image; version checks block downgrade where required.
- Options include the open-source bootloader MCUboot, TF-M (Trusted Firmware-M) on Cortex-M33 parts, and vendor secure-boot and secure-firmware-update packages for the families that offer them.

## TrustZone on Cortex-M33 parts

- The part is divided into secure and non-secure worlds. Memory, peripherals, and interrupts are assigned to one world through the security attribution units and the global TrustZone controller.
- Enabling TrustZone is controlled by an option byte and changes how the device starts (it boots in the secure world). Plan the project as two images (secure and non-secure) with the secure side exposing a small set of non-secure-callable entry functions.
- Keep the secure world small, validate every pointer and length crossing the boundary, and never expose secrets to non-secure callers.
- Reverting TrustZone may require read-out protection regression, which erases flash on some parts. Verify the procedure before relying on it.

## Keys and crypto hardware

Many parts have hardware blocks for random numbers, hashing, symmetric ciphers, and public-key acceleration, and some support protected key use. Use a maintained library or the vendor's secure services rather than custom crypto. Seed random numbers from the hardware generator and check its health flags. Do not derive keys from the unique device ID alone.

## Production and lifecycle

- Provision per-device keys and certificates in a controlled environment; record what was provisioned.
- Lock debug and apply protection as the last production step, then verify on the programmed unit.
- Define field return and failure analysis handling for locked devices.
- Define end-of-life and key compromise procedures.

## Verification

- Try attacks you plan to resist: connect a debugger, read flash, boot a modified image, install an old image, truncate an update, power-cycle during an update.
- Review the secure/non-secure interface for unchecked inputs.
- Record residual risks and who accepted them.
