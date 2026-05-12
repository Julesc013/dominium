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

### POST-CONVERGE-02 - Root Wrapper / Tooling / Governance Cleanup

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

### POST-CONVERGE-03 - Content / Pack / Profile / Bundle Cleanup

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

### POST-CONVERGE-04 - Compat / Lib / Specs / Security / Update Cleanup

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

### POST-CONVERGE-05 - Core / Control / Net Ownership Review

Scope:

- `core`
- `control`
- `net`

Goal:

- classify by actual ownership
- preserve process-only mutation, authority, runtime, network, and server semantics

### POST-CONVERGE-06 - Build and FAST Gate Remediation

Scope:

- verify preset/toolchain
- FAST xstack `repox_runner`
- AIDE pack compatibility

Goal:

- decide whether local verify requires Visual Studio 2022 or a Ninja fallback
- update CompatX schema discovery for post-CONVERGE schema locations if approved
- resolve AIDE Lite Python compatibility or document Python floor

### POST-CONVERGE-07 - Canonical Local Runtime/Playtest Proof

Scope:

- one canonical command sequence
- local authority/session/status/save/load/resume proof

Goal:

- prove runtime/playtest locally only after configure/build/test and FAST remediation are clean enough

## Success Target

Reduce active exceptions from 37 to under 15, then under 5, while preserving only genuinely intentional long-lived exceptions.
