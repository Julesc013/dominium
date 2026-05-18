Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Exception Retirement Queue

## Queue Policy

- one batch at a time
- no broad moves without inspection
- generated roots first
- high-risk semantic roots last
- every retired exception must update `contracts/repo/layout_exceptions.toml`
- every batch must run strict layout and root allowlist validators
- no feature work in exception retirement tasks

## Queue

### POST-CONVERGE-01 - Generated / Output Root Cleanup

Status: completed with review carryover.

Scope:

- `.xstack_cache`
- `artifacts`
- `build`
- `dist`
- `out`

Goal:

- remove tracked generated junk if safe
- confirm ignored/generated status
- preserve evidence/provenance where required
- update exception ledger

Result:

- Retired: `.xstack_cache`, `build`, `out`.
- Left active for review: `artifacts`, `dist`.
- Active exception count after cleanup: 34.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_01_GENERATED_OUTPUT_CLEANUP.md`.

Notes:

- `artifacts/` contains tracked toolchain-run provenance JSON and needs release/evidence policy review.
- `dist/` contains tracked distribution projection wrappers, locks, pack aliases, profile data, and `.gitkeep` files and needs distribution projection policy review.
- Python `__pycache__/` residue from validation was removed and `.gitignore` was tightened so broad source allow-list negations do not re-expose bytecode caches.

### POST-CONVERGE-02 - Root Wrapper / Tooling / Governance Cleanup

Status: completed with review carryover.

Scope:

- root command wrappers
- `__init__.py`
- `governance/`, `ide/`, `labs/`, `meta/`, `performance/`, and `validation/`
- `meta_extensions_engine.py`
- `numeric_discipline.py`

Goal:

- move to scripts/tools/docs/archive/contracts where safe
- remove root clutter
- update exception ledger

Result:

- Retired: `__init__.py`, `labs`.
- Moved: `labs/README.md` to `archive/historical/labs/README.md`.
- Compatibility shims kept: `tool_ui_bind.cmd`, `tool_ui_doc_annotate.cmd`, `tool_ui_validate.cmd`.
- Left active for protected review: `governance`, `ide`, `meta`, `meta_extensions_engine.py`, `numeric_discipline.py`, `performance`, `validation`.
- Active exception count after cleanup: 32.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_02_WRAPPER_TOOLING_CLEANUP.md`.

Notes:

- Root command wrappers remain documented zero-setup developer shims that resolve through `scripts/dev/tool_shim.py`.
- `governance/`, `meta/`, `meta_extensions_engine.py`, `numeric_discipline.py`, `performance/`, and `validation/` have active imports and were not moved by this cleanup task.
- `ide/` remains an intentional generated projection boundary with tracked manifest documentation.
- Next task: POST-CONVERGE-03.

### POST-CONVERGE-03 - Content / Pack / Profile / Bundle Cleanup

Status: completed with review carryover.

Scope:

- `data`
- `packs`
- `profiles`
- `bundles`
- `modding`
- `models`
- `templates`

Goal:

- split by ownership into content/contracts/docs/tests/release/archive
- preserve pack/profile IDs and compatibility semantics

Result:

- Retired: none.
- Moved: none.
- Left active for protected or identity-sensitive review: `data`, `packs`, `profiles`, `bundles`, `modding`, `models`, `templates`.
- Active exception count after cleanup: 32.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_03_CONTENT_PACK_CLEANUP.md`.

Notes:

- `data/` is mixed across registries, authored pack declarations, world/domain data, planning mirrors, generated evidence, baselines, release/runtime data, and XStack metadata.
- `packs/` remains the active runtime pack substrate; `data/packs/` remains scoped authored pack content/declaration authority and residual-quarantined for any single-root convergence.
- `content/profiles/bundles/bundle.mvp_default.json` embeds identity, hashes, and rel-path metadata and was not moved.
- `bundles/` remains active bundle profile source referenced by XStack/control tooling.
- `modding/` and `models/` are active Python implementation packages, not content-only roots.
- `templates/` remains active because safe relocation crosses protected specs/reality and XStack/AIDE contract references.
- Next task: POST-CONVERGE-04.

### POST-CONVERGE-04 - Compat / Lib / Specs / Security / Update Cleanup

Status: completed with protected review carryover.

Scope:

- `compat`
- `lib`
- `libs`
- `locks`
- `repo`
- `safety`
- `security`
- `specs`
- `updates`

Goal:

- inspect first
- split only pure subsets
- preserve trust/security/update/compat semantics

Result:

- Retired: none.
- Moved: none.
- Left active for protected or build/identity-sensitive review: `compat`, `lib`, `libs`, `locks`, `repo`, `safety`, `security`, `specs`, `updates`.
- Active exception count after cleanup: 32.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_04_COMPAT_LIB_SPEC_SECURITY_CLEANUP.md`.

Notes:

- `compat/` remains active implementation and shim code imported by client, server, runtime, tooling, and tests.
- `lib/` and `libs/` remain active implementation and build/ABI surfaces; no CMake target names, include paths, or ABI headers moved.
- `contracts/package/locks/pack_lock.mvp_default.json` remains a concrete source lock artifact with embedded identity and distribution copy behavior.
- `repo/` remains active release/control-plane material for release policy, RepoX rulesets, and canon state.
- `safety/`, `security/`, and `specs/` remain protected semantics surfaces; `specs/reality/` authority is preserved.
- `updates/` remains tracked RepoX-generated update feed material referenced by release/update tooling.
- Next task: POST-CONVERGE-05.

### POST-CONVERGE-05 - Core / Control / Net Ownership Review

Status: completed with protected review carryover.

Scope:

- `core`
- `control`
- `net`

Goal:

- classify by actual ownership
- preserve process-only mutation, authority, runtime, network, and server semantics

Result:

- Retired: none.
- Moved: none.
- Left active for protected review: `core`, `control`, `net`.
- Active exception count after cleanup: 32.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_05_CORE_CONTROL_NET_REVIEW.md`.
- Ownership note: `docs/repo/CORE_CONTROL_NET_OWNERSHIP.md`.

Notes:

- `core/` remains active deterministic substrate used by game domains, tools, and XStack session runtime.
- `control/` remains active control gateway, Control IR, negotiation, fidelity, planning, capability, view, effects, and proof implementation.
- `net/` remains active transport, server-authoritative, lockstep, SRZ hybrid, anti-cheat, shard coordination, and deterministic network test-harness implementation.
- Process-only mutation, authority, server, network protocol, anti-cheat, SRZ, resync, and replay semantics were not changed.
- Next task: POST-CONVERGE-06.

### POST-CONVERGE-06 - Build and FAST Gate Remediation

Status: partial, with targeted remediation completed.

Scope:

- verify preset/toolchain
- FAST xstack `repox_runner`
- AIDE pack compatibility

Goal:

- decide whether local verify requires Visual Studio 2022 or a Ninja fallback
- update CompatX schema discovery for post-CONVERGE schema locations if approved
- resolve AIDE Lite Python compatibility or document Python floor

Result:

- CMake verify: still blocked locally by missing Visual Studio 17 2022 instance.
- Build and CTest: not run because configure failed.
- Fallback preset: not added because no local compiler or Ninja/NMake/Make toolchain was discoverable.
- FAST: original `repox_runner` structural blocker fixed; remaining failure is broad RepoX `DRIFT`.
- AIDE: doctor, validate, and pack pass after the Python 3.8 newline writer compatibility fix.
- Audit: `docs/repo/audits/POST_CONVERGE_06_BUILD_FAST_REMEDIATION.md`.
- Build path docs: `docs/repo/BUILD_VERIFICATION_PATHS.md`.
- FAST remediation docs: `docs/repo/FAST_GATE_REMEDIATION.md`.
- AIDE remediation docs: `docs/repo/AIDE_PACK_REMEDIATION.md`.

Notes:

- CompatX schema discovery now prefers `contracts/schemas/` and keeps legacy `schemas/` fallback.
- RepoX worldgen path references were updated to canonical `game/domains/...` paths.
- The remaining FAST drift backlog is too broad for exception retirement or build remediation scope.
- Next task remains blocked until build proof and FAST drift are resolved or explicitly accepted by review.

### POST-CONVERGE-07 - Canonical Local Runtime/Playtest Proof

Scope:

- one canonical command sequence
- local authority/session/status/save/load/resume proof

Goal:

- prove runtime/playtest locally only after configure/build/test and FAST remediation are clean enough

## Success Target

Reduce active exceptions from 37 to under 15, then under 5, while preserving only genuinely intentional long-lived exceptions.
