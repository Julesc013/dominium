Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# POST-CONVERGE-04 Compat / Lib / Specs / Security / Update Cleanup

## Status

- Task ID: POST-CONVERGE-04
- Result: pass
- Date/time: 2026-05-12T20:12:03.8149725+10:00
- Branch: `main`
- HEAD SHA: `ed571cd32cd9c5ec53786f24919f87d64710f031`
- origin/main SHA: `ed571cd32cd9c5ec53786f24919f87d64710f031`
- Working tree status before task: clean, synced with `origin/main`
- Working tree status after task: documentation, exception ledger, inventory, and move-map metadata updated; no target root bytes moved

## Scope

This task targeted only:

- `compat`
- `lib`
- `libs`
- `locks`
- `repo`
- `safety`
- `security`
- `specs`
- `updates`

Explicit non-actions:

- no product roots moved
- no runtime roots moved
- no core/control/net roots moved
- no domain roots moved
- no pack/profile/content roots moved
- no build semantics changed
- no compatibility/security/safety/update semantics changed
- no feature work performed

## Pre-Cleanup State

| Path | Exists? | Tracked? | Referenced? | Classification | Notes |
| --- | --- | --- | --- | --- | --- |
| `compat` | yes | yes, 17 files | yes | protected_review | Active Python compatibility implementation, negotiation/handshake helpers, migration/refusal helpers, and shims are imported by client, server, runtime, tools, and tests. |
| `lib` | yes | yes, 22 files | yes | protected_review | Active Python install, instance, save, store, bundle, import/export, and artifact implementation is imported by runtime, tools, and tests. |
| `libs` | yes | yes, 86 files | yes | protected_review | CMake targets, C/C++ libraries, UI backend code, build identity code, and public `dom_contracts` ABI headers are build/interface sensitive. |
| `locks` | yes | yes, 1 file | yes | protected_review | `locks/pack_lock.mvp_default.json` is a concrete pack lock artifact with embedded identity, hash, ordered pack, and rel-path semantics. |
| `repo` | yes | yes, 11 files | yes | protected_review | Contains active release policy, RepoX rulesets/exemptions, and canon state control-plane material. |
| `safety` | yes | yes, 2 files | yes | protected_review | Active safety engine implementation and refusal/pattern semantics are imported by domain logic and backed by docs/schemas. |
| `security` | yes | yes, 4 files | yes | protected_review | Active trust and license-capability implementation is referenced by release, tooling, docs, and schema surfaces. |
| `specs` | yes | yes, 9 files | yes | protected_review | Contains active `spec_engine.py` imports and canonical `specs/reality` normative specs. |
| `updates` | yes | yes, 6 files | yes | protected_review | Tracked RepoX-generated update feeds are referenced by release/update tooling, tests, command registry, and release docs. |

## Ownership Classification

| Path | Contracts | Docs | Tools | Release | Tests | External | Runtime/Implementation | Generated | Review Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `compat` | possible future pure contracts | docs reference it | tooling imports it | no | tests import it | no | yes | no | Leave active; moving would alter compatibility import and shim semantics. |
| `lib` | no pure subset moved | docs reference it | tools import it | no | tests import it | no | yes | no | Leave active; moving crosses install/save/store/runtime semantics. |
| `libs` | public ABI headers present | docs reference it | build/ABI validators inspect it | no | tests/build reference it | no | yes | no | Leave active; moving crosses CMake targets, include paths, and ABI boundaries. |
| `locks` | lock contracts belong in `contracts/locks` | docs reference it | distribution tooling consumes it | bundle copy behavior | tests/distribution reference it | no | concrete source artifact | no | Leave active; not a pure lockfile contract and path identity is embedded. |
| `repo` | some concepts map to `contracts/repo` | docs reference it | RepoX rulesets support tooling | release policy present | no | no | control-plane material | no | Leave active; release policy and RepoX control-plane semantics need protected review. |
| `safety` | possible future safety contracts | docs/schemas reference it | no pure tooling subset moved | no | domain/tests reference it | no | yes | no | Leave active; safety semantics are protected. |
| `security` | possible future security contracts | docs/schemas reference it | security/release tooling references it | trust/release linkage | tests/docs reference it | no | yes | no | Leave active; trust/signing/capability semantics are protected. |
| `specs` | possible future contract-bound specs | docs reference it | tools import it | no | tests import it | no | active spec engine plus normative specs | no | Leave active; `specs/reality` authority must not be demoted. |
| `updates` | possible future update/distribution contracts | docs reference it | release/update tooling consumes it | update feeds | tests reference it | no | no | tracked generated feeds | Leave active; feed generation and update identity need release review. |

## Actions Taken

| Path | Action | New Location(s) | Compatibility Shim? | Exception Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `compat` | narrowed_exception | none | no | active | No move; exception reason now names active implementation, migration/refusal, and shim references. |
| `lib` | narrowed_exception | none | no | active | No move; exception now records active Python library implementation and import compatibility. |
| `libs` | narrowed_exception | none | no | active | No move; exception now records CMake/ABI/public-header sensitivity. |
| `locks` | narrowed_exception | none | no | active | No move; exception now records concrete pack lock artifact identity. |
| `repo` | narrowed_exception | none | no | active | No move; exception now records release policy, RepoX, and canon state ownership. |
| `safety` | narrowed_exception | none | no | active | No move; exception now records active safety engine semantics. |
| `security` | narrowed_exception | none | no | active | No move; exception now records active trust/license capability semantics. |
| `specs` | narrowed_exception | none | no | active | No move; exception now records active spec engine imports and `specs/reality` authority. |
| `updates` | narrowed_exception | none | no | active | No move; exception now records tracked generated update feeds and release/update references. |

## Protected Semantics Check

- compatibility semantics changed? no
- security/trust/signing semantics changed? no
- safety semantics changed? no
- update semantics changed? no
- lockfile semantics changed? no
- ABI/build semantics changed? no

## Reference Updates

- docs updated: yes, to record POST-CONVERGE-04 classification and protected review carryover
- scripts updated: no updates needed
- validators updated: no updates needed
- tests updated: no updates needed
- no direct code references were changed because no target root bytes moved

## Exception Ledger Changes

| Exception ID | Path | Previous Active? | New Active? | New Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `compat_root` | `compat` | yes | yes | protected_review | Active compatibility implementation and shims remain. |
| `lib_root` | `lib` | yes | yes | protected_review | Active Python implementation remains. |
| `libs_root` | `libs` | yes | yes | protected_review | CMake/ABI/public-header surface remains. |
| `locks_root` | `locks` | yes | yes | protected_review | Concrete source pack lock artifact remains. |
| `repo_root` | `repo` | yes | yes | protected_review | Release policy, RepoX rulesets, and canon state remain. |
| `safety_root` | `safety` | yes | yes | protected_review | Active safety implementation remains. |
| `security_root` | `security` | yes | yes | protected_review | Active trust implementation remains. |
| `specs_root` | `specs` | yes | yes | protected_review | Active spec engine and `specs/reality` authority remain. |
| `updates_root` | `updates` | yes | yes | protected_review | Tracked RepoX update feeds remain. |

## Remaining High-Risk Exceptions

All target exceptions remain active:

- `compat_root`: active compatibility implementation and shim imports.
- `lib_root`: active Python install/save/store/bundle/artifact implementation.
- `libs_root`: build/ABI-sensitive C/C++ library and public contract headers.
- `locks_root`: concrete identity-bearing pack lock artifact.
- `repo_root`: release/control-plane policy and RepoX material.
- `safety_root`: protected safety implementation and policy semantics.
- `security_root`: protected trust/signing/license capability semantics.
- `specs_root`: active spec engine plus canonical `specs/reality` normative authority.
- `updates_root`: tracked generated update feeds with release/update references.

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
| `git diff --cached --check` | pass; no staged changes at validation time |

Supplemental preflight:

- `python .aide/scripts/aide_lite.py doctor`: pass with existing warnings.
- `python .aide/scripts/aide_lite.py validate`: pass with existing review-packet warnings.
- `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-04 compat lib spec security update cleanup"`: failed with the known Python 3.8 `Path.write_text(newline=...)` compatibility issue documented in prior post-CONVERGE audits.

## Risks

- security/safety/spec roots remain active due to protected semantics
- `lib`/`libs` remain active due to implementation, build, and ABI ambiguity
- `locks` remains active due to concrete lock artifact identity semantics
- `updates` remains active because tracked generated feeds are tied to release/update tooling
- no build/FAST remediation was attempted

## Next Recommended Task

`POST-CONVERGE-05 - Core / Control / Net Ownership Review`
