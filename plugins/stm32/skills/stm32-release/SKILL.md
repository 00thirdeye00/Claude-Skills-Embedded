---
name: stm32-release
description: STM32-specific release and production checklist: option bytes (read-out protection, write protection, brown-out level, watchdog mode, boot configuration), flash layout and CRC, version stamping, watchdog policy, unique ID and calibration handling, production programming with a programmer tool, and verification of protection settings. Use when preparing an STM32 firmware release or production build, or when deciding read-out protection and debug policy. Trigger with "STM32 release checklist", "option bytes for production", "read-out protection", "RDP level", "lock the debug port", "factory programming STM32", "watchdog hardware mode".
argument-hint: "<product, STM32 part, production process, security and update needs>"
---

# /stm32:stm32-release

Check an STM32 firmware release and its production setup.

## Usage

```
/stm32:stm32-release $ARGUMENTS
```

If details are missing, ask for the part, whether a bootloader and field updates exist, the security policy for debug access, and how devices are programmed in production.

## How It Works

```
┌──────────────────────────────────────────────────────────┐
│ 1 GENERIC    embedded release checklist                   │
│ 2 OPTION BYTES   protection, BOR, watchdog, boot          │
│ 3 IMAGE      layout, CRC, version, signing                │
│ 4 PRODUCTION programming steps and verification           │
│ 5 DECISION   GO / NO-GO with blockers                     │
└──────────────────────────────────────────────────────────┘
```

## Steps

1. **Apply the generic checklist.** With `embedded-core` installed, use `/embedded-core:embedded-release`; otherwise use the items summarized here.
2. **Review option bytes** with `references/option-bytes-and-protection.md`. List each setting, its intended value, and why.
3. **Review image details**: linker regions versus the part, version string, CRC or signature, vector table address, bootloader compatibility.
4. **Review production**: programming tool and script, unique data per unit, post-programming verification, and a test that read-back protection works as intended.
5. **Decide**: list blockers, and give GO, NO-GO, or GO WITH CONDITIONS.

## Output

```markdown
## STM32 Release Check: [product] v[version]

### Recommendation: GO / NO-GO / GO WITH CONDITIONS

### Option bytes
| Setting | Intended value | Verified | Reason |
|---|---|---|---|

### Image and layout
| Item | Status | Notes |
|---|---|---|

### Production
| Step | Status | Notes |
|---|---|---|

### Blockers and conditions
- [..]
```

## Rules

- Do not apply or recommend applying irreversible protection (the highest read-out protection level) without explicit confirmation from the user, who must confirm it was tested on sacrificial units first.
- Take option-byte names, encodings, and consequences from the reference manual for the exact part; encodings differ between families.
- Treat anything unverified as not passed.

## If Connectors Available

If **~~source control** is connected:
- Verify the release tag, build configuration, and archived artifacts.

If **~~project tracker** is connected:
- Check for open release-blocking issues.

## Tips

1. **Test protection settings on a spare unit** and confirm you can still recover or reprogram as planned.
2. **Read option bytes back** after programming, in the production flow.
3. **Archive the ELF and map file** with each release for field crash analysis.
