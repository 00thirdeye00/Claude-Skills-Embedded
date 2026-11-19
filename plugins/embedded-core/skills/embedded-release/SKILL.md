---
name: embedded-release
description: Pre-release verification checklist for embedded firmware on any MCU: reproducible build, version stamping, memory and flash layout checks, image integrity and signing, watchdog and brown-out settings, bootloader and update safety, debug-port policy, production programming, and field-update tests. Use when preparing a firmware release, a production build, or an over-the-air update, or when writing a go/no-go checklist. Trigger with "release checklist", "ready to ship firmware", "production build", "OTA update safety", "what could go wrong in the field".
argument-hint: "<release description: product, MCU, update method, target date>"
---

# /embedded-core:embedded-release

Produce and walk a go/no-go checklist for shipping firmware, including factory programming and field updates.

## Usage

```
/embedded-core:embedded-release $ARGUMENTS
```

If no context is given, ask for the product, MCU, how devices are programmed in production, and whether firmware updates in the field.

## Workflow

1. **Collect release facts**: version, hardware revisions supported, update path, bootloader version, known issues.
2. **Walk** `references/release-checklist.md`, marking each item Pass, Fail, N/A, or Unknown.
3. **Flag blockers**: any Fail or Unknown on integrity, update safety, or protection settings blocks release.
4. **Report** with the output template and a clear recommendation.

## Output

```markdown
## Release Check: [product] v[version]

### Recommendation: GO / NO-GO / GO WITH CONDITIONS

### Checklist
| Area | Item | Status | Notes |
|---|---|---|---|

### Blockers
- [item and what must happen]

### Rollback plan
[how to recover a bad release in the field]
```

## Rules

- Treat Unknown as not passed until someone verifies it.
- Update safety covers power loss at any point of the update; test it, do not assume it.
- Archive the exact ELF, map file, toolchain version, and build configuration for every release.
- Production protection settings that cannot be undone need an explicit decision from the owner.

## If Connectors Available

If **~~source control** is connected:
- Verify the tag, the commit, and that CI passed for the release candidate.

If **~~project tracker** is connected:
- Check that no open blocking issues target this release.

## Tips

1. **Test the update path from the previous shipped version**, not only from the last build.
2. **Run the release candidate unmodified** through the full test, with release build flags.
3. **Write the rollback plan before shipping**, not after the first field failure.
