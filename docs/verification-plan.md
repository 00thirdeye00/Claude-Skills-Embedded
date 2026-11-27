# Verification plan: facts, installs, and triggers

This plan covers backlog items B-003 (audit against manuals) and B-004 (install and behavior tests). It is a plan, not a result: none of it has been done.

## Contents
- B-003: audit facts against manuals
- B-004: install, trigger, and orchestrator tests
- Evidence to keep
- Exit criteria

## B-003: audit facts against manuals

**Goal:** every family-level statement in the references is confirmed, corrected, or marked unverified, with a source.

**Needs:** someone with the ST reference manuals, datasheets, errata sheets, and application notes for each family, and ideally a board per family.

**Method**
1. List the claims. Search the references for statements about register names, bit positions, option-byte encodings, mode names, DMA and clock limits, peripheral behavior, and numbers. Record each in a table: claim, file, family, source document and section, status (confirmed, corrected, unverifiable), reviewer, date.
2. Prioritize by risk: option bytes and read-out protection, flash and bootloader facts, clock and voltage limits, DMA reach and cache, fault-register behavior, then the rest.
3. Start with the families most used: F4, G4, L4, H7, U5. Review one family at a time, so a reviewer holds one manual set.
4. Correct the text, or replace a numeric claim with "see the reference manual section X" when the value varies by part.
5. Sample on hardware: pick the 10 highest-risk claims per family and test them on a board (for example the system bootloader entry method, flash erase sizes, DMA reachability, the CRC parameters, wake-up behavior).
6. Mark the references with the audit date and manual revisions.

**Output:** an audit table in `docs/audit/<family>.md`, corrected references, and updated backlog rows.

**Effort:** a few hours per family for the table and corrections, plus bench time for the hardware sample.

## B-004: install, trigger, and orchestrator tests

**Environments:** Claude Code (command line), the Claude desktop app (marketplace add and zip upload), claude.ai (single-skill upload).

| # | Test | Pass criterion |
|---|---|---|
| 1 | `claude plugin validate .` on the repository | No errors |
| 2 | Add the marketplace and install `stm32` and `embedded-core` | Plugins listed; skills appear as `/stm32:...` and `/embedded-core:...` |
| 3 | Check that manual-only skills stay out of the model's skill list and do not run on their own | A debugging question without a command does not load a skill; the context view shows no skill descriptions |
| 4 | Measure context cost: start a conversation with the plugins installed, check context usage before and after calling one command | Idle overhead is near zero; the command cost is close to the estimates in the README |
| 5 | Call each of the 24 commands once with a small input | Each loads, follows its steps, and reads its references by relative path |
| 6 | Run the scripts through the skills (fault decode, pin map, map summary, stack usage, architecture check) on real files | Outputs match the tools' own reports |
| 7 | Orchestrator self-run: give a multi-stage goal, approve, and watch it read sibling skill files | It finds `../<skill>/SKILL.md`, runs stages in order, writes `firmware-plan.md`, and logs a gap to the backlog when a stage has no skill |
| 8 | Orchestrator across plugins: `embedded-orchestrator` with and without `stm32` installed | It finds or reports missing skills correctly |
| 9 | Hand-off mode | It outputs correct commands without reading skills |
| 10 | Desktop app and claude.ai behavior of the manual-only setting | Record whether skills are listed or auto-loaded; adjust the README |
| 11 | Upload a single skill zip to claude.ai | It loads and its references are found |

**Fixes feed back** into the README (install steps, menu names, caveats) and the backlog.

## Evidence to keep

Command outputs, screenshots of the skill and context views, the versions of Claude Code and the desktop app, the date, and notes on any difference from the README. Store them in `docs/audit/` or an issue.

## Exit criteria

- B-003: every priority family has an audit table, and no unconfirmed claim remains without an "unverified" mark.
- B-004: tests 1 to 9 pass in Claude Code; tests 10 and 11 are recorded for the other apps; the README matches observed behavior.
