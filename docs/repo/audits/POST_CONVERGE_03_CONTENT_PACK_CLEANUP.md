# POST-CONVERGE-03 Content / Pack / Profile / Bundle Cleanup

## Status

- Task ID: POST-CONVERGE-03
- Result: pass with review carryover
- Date/time: 2026-05-12T19:53:09.1644049+10:00
- Branch: `main`
- HEAD SHA: `e81e6d7f2a97af5e3c0fe2d26736d8e4cf9e66a6`
- origin/main SHA: `e81e6d7f2a97af5e3c0fe2d26736d8e4cf9e66a6`
- Working tree status before task: clean after POST-CONVERGE-02; no unrelated local changes were present.
- Sync status: `git fetch origin` and `git pull --ff-only origin main` completed with `Already up to date.`
- Working tree status after task: POST-CONVERGE-03 documentation, exception-ledger, inventory, and move-map changes only.

## Scope

This task targeted only:

- `data`
- `packs`
- `profiles`
- `bundles`
- `modding`
- `models`
- `templates`

Scope constraints upheld:

- no product roots moved
- no runtime roots moved
- no core/control/net roots moved
- no security/safety/spec/update roots moved
- no build semantics changed
- no pack, profile, or bundle IDs changed
- no source semantics changed
- no feature work performed

## Pre-Cleanup State

| Path | Exists? | Tracked? | Referenced? | Classification | Notes |
| --- | --- | --- | --- | --- | --- |
| `data` | yes | yes | yes | `unknown_mixed_review` | 1,279 tracked files across registries, `data/packs`, planning mirrors, audit/baseline material, world/domain data, release/runtime data, and XStack metadata. |
| `packs` | yes | yes | yes | `protected_identity_review` | 256 tracked files; active pack substrate with `pack.json`, compatibility, trust, and capability sidecars. |
| `profiles` | yes | yes | yes | `protected_identity_review` | Contains `profiles/bundles/bundle.mvp_default.json` with profile bundle identity, fingerprint, content hash, and rel-path metadata. |
| `bundles` | yes | yes | yes | `protected_identity_review` | Contains `bundle.base.lab` and `bundle.null` bundle definitions plus bundle docs. |
| `modding` | yes | yes | yes | `protected_identity_review` | Active Python mod trust/capability policy implementation imported by server, pack compatibility, MVP runtime bundle, and XStack tooling. |
| `models` | yes | yes | yes | `protected_identity_review` | Active Python constitutive model implementation imported by engine, game domains, meta reference logic, and tests. |
| `templates` | yes | yes | yes | `protected_reference_review` | Root templates are referenced by protected `specs/reality` and XStack/AIDE contract surfaces. |

## Ownership Classification

| Path | Content | Contracts | Docs | Tests | Release | Generated | Runtime-like | Review Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `data` | yes | yes | yes | yes | yes | yes | yes | Mixed by file family; `data/packs` remains scoped authored pack content/declaration authority and residual-quarantined for single-root convergence. |
| `packs` | yes | yes | yes | no | yes | possible | yes | Active runtime pack substrate; `packs/` and `data/packs/` scopes must not be collapsed without protected review. |
| `profiles` | yes | no | no | no | yes | no | yes | Identity metadata and rel-path references require review before relocation. |
| `bundles` | yes | possible | yes | no | yes | no | yes | Bundle IDs and dependency/lock semantics require review before relocation. |
| `modding` | no | possible | no | no | no | no | no | Active implementation package, not docs-only modding content. |
| `models` | no | possible | no | yes | no | no | no | Active implementation package, not authored model asset content. |
| `templates` | possible | possible | yes | no | no | no | no | Protected references must move first or be reviewed in the same task. |

## Actions Taken

| Path | Action | New Location(s) | Compatibility Shim? | Exception Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `data` | `left_for_review`; `narrowed_exception` | none | no | active | Kept for file-family split review. |
| `packs` | `left_for_review`; `narrowed_exception` | none | no | active | Kept to preserve active runtime pack substrate semantics. |
| `profiles` | `left_for_review`; `narrowed_exception` | none | no | active | Kept to preserve profile bundle identity, hashes, and rel-path metadata. |
| `bundles` | `left_for_review`; `narrowed_exception` | none | no | active | Kept to preserve bundle IDs and lock/dependency semantics. |
| `modding` | `left_for_review`; `narrowed_exception` | none | no | active | Kept because it is active imported implementation. |
| `models` | `left_for_review`; `narrowed_exception` | none | no | active | Kept because it is active imported implementation. |
| `templates` | `left_for_review`; `narrowed_exception` | none | no | active | Kept because protected references still bind to root templates. |
| `content/README.md` | `created` | `content/README.md` | no | not an exception | Defines intended authored-content ownership without moving identity-sensitive material. |
| `content/MANIFEST.md` | `created` | `content/MANIFEST.md` | no | not an exception | Records that POST-CONVERGE-03 performed review and no physical content moves. |

## Identity Preservation

- Pack IDs changed? no
- Profile IDs changed? no
- Bundle IDs changed? no
- Install/save/runtime identity changed? no
- Content hashes affected? no content files were moved or rewritten; only repository documentation and exception metadata changed.

## Reference Updates

- Updated `contracts/repo/layout_exceptions.toml` to narrow the seven target active exceptions.
- Updated `docs/repo/LAYOUT_EXCEPTION_LEDGER.md` and `docs/repo/EXCEPTION_RETIREMENT_QUEUE.md`.
- Added `content/README.md` and `content/MANIFEST.md`.
- Updated `docs/repo/ROOT_INVENTORY.md`, `docs/repo/MOVE_MAP.md`, `docs/repo/ROOT_FILE_POLICY.md`, and `docs/repo/OWNERSHIP_RULES.md` with POST-CONVERGE-03 status notes.
- Refreshed `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json`.
- No script, workflow, validator, or test path references were changed because no target root moved.

## Exception Ledger Changes

| Exception ID | Path | Previous Active? | New Active? | New Status | Notes |
| --- | --- | --- | --- | --- | --- |
| `data_root` | `data` | yes | yes | narrowed | Mixed file-family review remains required. |
| `packs_root` | `packs` | yes | yes | narrowed | Runtime pack substrate scope preserved. |
| `profiles_root` | `profiles` | yes | yes | narrowed | Profile identity and hash metadata preserved. |
| `bundles_root` | `bundles` | yes | yes | narrowed | Bundle IDs and lock semantics preserved. |
| `modding_root` | `modding` | yes | yes | narrowed | Active imported policy implementation. |
| `models_root` | `models` | yes | yes | narrowed | Active imported model implementation. |
| `templates_root` | `templates` | yes | yes | narrowed | Protected template references remain live. |

## Remaining Content / Pack / Profile / Bundle Exceptions

- `data_root`: remains active because the root mixes authored data, registries, generated evidence, planning mirrors, baseline material, runtime/release-like data, and XStack metadata.
- `packs_root`: remains active because it is the runtime pack substrate; `data/packs` remains scoped authored pack content/declaration material.
- `profiles_root`: remains active because the profile bundle embeds identity, fingerprint, content hash, and rel-path metadata.
- `bundles_root`: remains active because bundle IDs and lock/dependency semantics are live.
- `modding_root`: remains active because it is imported implementation, not docs-only or authored mod content.
- `models_root`: remains active because it is imported implementation, not authored model asset content.
- `templates_root`: remains active because protected `specs/reality` and XStack/AIDE contract references still point to it.

## Validation

Validation commands and results are recorded after the final POST-CONVERGE-03 validation pass:

| Command | Result |
| --- | --- |
| `python .aide/scripts/aide_lite.py doctor` | PASS |
| `python .aide/scripts/aide_lite.py validate` | PASS with existing review-packet warnings |
| `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-03 content pack profile bundle cleanup"` | FAILED with existing Python 3.8 `Path.write_text(newline=...)` incompatibility |
| `python tools/validators/check_repo_layout.py --repo-root .` | PASS; active exceptions 32, unexcepted violations 0 |
| `python tools/validators/check_repo_layout.py --repo-root . --json` | PASS; active exceptions 32, unexcepted violations 0 |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | PASS; strict result pass |
| `python tools/validators/check_root_allowlist.py --repo-root .` | PASS; active exceptions 32, unexcepted violations 0 |
| `python tools/validators/check_root_allowlist.py --repo-root . --json` | PASS; active exceptions 32, unexcepted violations 0 |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | PASS; strict result pass |
| `python tools/validators/check_distribution_layout.py --repo-root .` | PASS; warnings 0 |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | PASS; strict result pass |
| `python tools/validators/check_component_matrices.py --repo-root .` | PASS; warnings 0 |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | PASS; strict result pass |
| `python scripts/verify_docs_sanity.py --repo-root .` | PASS; Docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | PASS; build boundary checks passed |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | PASS; UI shell purity OK |
| `python scripts/verify_abi_boundaries.py --repo-root .` | PASS; ABI boundary check OK |
| `python -m json.tool tools/migration/root_inventory.json` | PASS |
| `python -m json.tool tools/migration/root_move_map.json` | PASS |
| `git diff --check` | PASS; only expected LF-to-CRLF working-copy warnings from Git |
| `git diff --cached --check` | PASS |

## Risks

- Pack, profile, and bundle roots remain active because identity-sensitive semantics require protected review.
- `data/` remains mixed and requires file-family review before any split.
- Generated/runtime-like material may still be present under mixed roots and remains under review.
- No build or FAST remediation was attempted.

## Next Recommended Task

`POST-CONVERGE-04 — Compat / Lib / Specs / Security / Update Cleanup`
