Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# POST-CONVERGE-05 Core / Control / Net Ownership Review

## Status

- Task ID: POST-CONVERGE-05
- Result: pass
- Date/time: 2026-05-12T20:27:16.3483009+10:00
- Branch: `main`
- HEAD SHA: `44bf83626fd1efade2d8e96ffe5bf8497a5aed3b`
- origin/main SHA: `44bf83626fd1efade2d8e96ffe5bf8497a5aed3b`
- Working tree status before task: clean, synced with `origin/main`
- Working tree status after task: documentation, exception ledger, inventory, and move-map metadata updated; no target root bytes moved

## Scope

This task targeted only:

- `core`
- `control`
- `net`

Explicit non-actions:

- no product roots moved
- no broad runtime roots moved
- no broad engine roots moved
- no domain roots moved
- no content/pack/profile roots moved
- no build semantics changed
- no process-only mutation semantics changed
- no authority semantics changed
- no network/server/SRZ/anti-cheat semantics changed
- no feature work performed

## Pre-Review State

| Path | Exists? | Tracked? | Referenced? | Classification | Notes |
| --- | --- | --- | --- | --- | --- |
| `core` | yes | yes, 16 files | yes, 19 Python import-reference files | protected_review | Deterministic substrate helpers for constraints, flow, graph/routing, hazards, schedules, spatial transforms, and state machines are used by game domains, tools, and XStack. |
| `control` | yes | yes, 21 files | yes, 19 Python import-reference files | protected_review | Control gateway, Control IR, negotiation, fidelity, planning, capability, view, effects, and proof implementation is used by apps/client, domains, net policy code, tools, and XStack. |
| `net` | yes | yes, 17 files | yes, 14 Python import-reference files | protected_review | Transport, server-authoritative, lockstep, SRZ hybrid, anti-cheat, shard coordination, and deterministic test-harness modules are used by apps/client, apps/server, tools, and XStack tests. |

## Ownership Classification

| Path | Engine | Game | Runtime | Apps/Server | Contracts | Docs | Tools | Tests | Generated | Review Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `core` | likely target for universal deterministic substrate | domains consume it | no clear runtime-only subset | no | possible future schemas/contracts only after split | docs reference it | tools consume it | tests cover it through XStack | no | Leave active; moving would change imports across domain and tooling surfaces. |
| `control` | no broad engine target | domains consume control effects/fidelity/capability | possible future runtime control adapters only after split | apps/client consumes gateway | possible future control contracts only after split | docs/control explains doctrine | tools consume stress/determinism paths | XStack tests cover it | no | Leave active; process-only mutation and authority gates require protected review. |
| `net` | no broad engine target | game proof hashes feed net policy | possible future runtime/network target for transports | apps/client and apps/server consume policy/transport | possible future network protocol contracts only after split | architecture/server docs reference it | tools consume it | XStack network tests consume it | no | Leave active; server authority, anti-cheat, SRZ, resync, and replay semantics require protected review. |

## Actions Taken

| Path | Action | New Location(s) | Compatibility Shim? | Exception Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `core` | narrowed_exception | none | no | active | No move; exception reason now names deterministic substrate helpers and live domain/tool/XStack references. |
| `control` | narrowed_exception | none | no | active | No move; exception reason now names active control gateway, IR, negotiation, fidelity, planning, capability, view, effects, and proof references. |
| `net` | narrowed_exception | none | no | active | No move; exception reason now names active transport, server-authoritative, lockstep, SRZ, anti-cheat, shard coordination, and test-harness references. |
| `docs/repo/CORE_CONTROL_NET_OWNERSHIP.md` | created | `docs/repo/CORE_CONTROL_NET_OWNERSHIP.md` | no | not an exception | Records ownership rules and invariants for later protected relocation work. |

## Protected Semantics Check

- process-only mutation semantics changed? no
- authority/control semantics changed? no
- network protocol semantics changed? no
- server semantics changed? no
- anti-cheat/integrity semantics changed? no
- SRZ/shard/resync semantics changed? no
- ABI/build semantics changed? no

## Reference Updates

- docs updated: yes, to record POST-CONVERGE-05 classification and protected review carryover
- scripts updated: no updates needed
- validators updated: no updates needed
- tests updated: no updates needed
- no direct code references were changed because no target root bytes moved

## Exception Ledger Changes

| Exception ID | Path | Previous Active? | New Active? | New Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `core_root` | `core` | yes | yes | protected_review | Active deterministic substrate remains. |
| `control_root` | `control` | yes | yes | protected_review | Active control gateway, IR, proof, and authority-sensitive implementation remains. |
| `net_root` | `net` | yes | yes | protected_review | Active network/server/SRZ/anti-cheat implementation remains. |

## Remaining Core / Control / Net Exceptions

All target exceptions remain active:

- `core_root`: deterministic substrate imports are live across domain and tooling surfaces.
- `control_root`: process-only mutation, authority gates, control proof, and Control IR semantics are protected.
- `net_root`: network transport, server authority, anti-cheat, SRZ/shard, resync, replay, and test-harness semantics are protected.

## Validation

Validation was run after the metadata updates:

| Command | Result |
| --- | --- |
| `python tools/validators/check_repo_layout.py --repo-root .` | pass |
| `python tools/validators/check_repo_layout.py --repo-root . --json` | pass |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass |
| `python tools/validators/check_root_allowlist.py --repo-root .` | pass |
| `python tools/validators/check_root_allowlist.py --repo-root . --json` | pass |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass |
| `python tools/validators/check_distribution_layout.py --repo-root .` | pass |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass |
| `python tools/validators/check_component_matrices.py --repo-root .` | pass |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass |
| `git diff --check` | pass |
| `git diff --cached --check` | pass |

Supplemental preflight:

- `python .aide/scripts/aide_lite.py doctor`: pass with existing warnings.
- `python .aide/scripts/aide_lite.py validate`: pass with existing review-packet warnings.
- `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-05 core control net ownership review"`: failed with the known Python 3.8 `Path.write_text(newline=...)` compatibility issue documented in prior post-CONVERGE audits.

## Risks

- `core`, `control`, and `net` remain active due to protected semantics and live imports.
- build/runtime path references may require later remediation if a future task performs physical relocation.
- no build/FAST remediation was attempted.

## Next Recommended Task

`POST-CONVERGE-06 - Build and FAST Gate Remediation`
