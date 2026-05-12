# Layout Enforcement

Status: PROVISIONAL

Phase: CONVERGE-10

Machine-readable authority:

- `contracts/repo/layout.contract.toml`
- `contracts/repo/root_allowlist.toml`
- `contracts/repo/layout_exceptions.toml`

## Purpose

CONVERGE-10 makes strict source repository layout validation meaningful. Default validator runs remain audit-friendly and exit zero for reporting, but strict mode now blocks unexcepted root-level drift.

Source repository layout enforcement does not change runtime, install, media, package, save, cache, staging, or distribution projections. Those layouts remain governed by distribution and runtime projection contracts.

## Audit And Strict Modes

Audit mode reads the layout contract, root allowlist, and exception ledger, then reports root classifications, generated roots, exceptions, and potential strict violations. Audit mode exits zero unless the validator itself cannot run.

Strict mode applies the same checks but fails when a remaining violation has no active exception. Strict mode is intended for local gates and CI-style validation surfaces after CONVERGE-10.

Run locally:

```bash
python tools/validators/check_repo_layout.py --repo-root .
python tools/validators/check_repo_layout.py --repo-root . --strict
python tools/validators/check_root_allowlist.py --repo-root .
python tools/validators/check_root_allowlist.py --repo-root . --strict
python tools/validators/check_distribution_layout.py --repo-root . --strict
```

## What Strict Mode Blocks

Strict mode blocks:

- unknown root-level directories or files without an active exception
- new product roots outside `apps/`
- new domain roots outside the contracts/game/content/docs/tests split
- new schema or registry roots outside `contracts/`
- new runtime adapter roots outside `runtime/`
- generated roots without generated policy or active exception
- retired roots recreated after their convergence phase
- malformed contracts or malformed exception ledgers

## Exceptions

Temporary exceptions live in `contracts/repo/layout_exceptions.toml`.

Every active exception must have:

- stable exception ID
- path
- kind
- classification
- reason
- target or review target
- retirement phase
- risk
- notes

Exceptions are not permanent authority. They are named proof that a root remains unresolved and must be reviewed in the named retirement phase. Broad wildcard exceptions are forbidden unless a later reviewed task explicitly authorizes them.

## Adding An Exception

To add a temporary exception:

1. Add one `[exceptions.<stable_id>]` entry to `contracts/repo/layout_exceptions.toml`.
2. Set `active = true`.
3. Give a specific path, reason, target, risk, and retirement phase.
4. Update `docs/repo/LAYOUT_EXCEPTION_LEDGER.md`.
5. Run both strict validators.

Do not add an exception to make a new root convenient. New roots should normally be added under the existing canonical ownership roots.

## Gate Intent

The intended strict validation surface is:

- `python tools/validators/check_repo_layout.py --repo-root . --strict`
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`

CONVERGE-10 does not change branch protection and does not make CMake configure fail by default. A later gate or CI change may invoke these strict commands explicitly.

## CONVERGE-11 Matrix Expansion

Component matrices are governed by:

- `contracts/release/component_matrix.contract.toml`
- `tools/validators/check_component_matrices.py`
- `docs/release/COMPONENT_MATRIX.md`

Matrix expansion must not create new root-level directories outside the layout contract and exception ledger. New platform, render, native shell, audio, input, network, and storage implementation belongs under existing ownership roots, especially `runtime/`, `apps/`, `contracts/`, `content/`, and `tools/`.

Matrix status values are support posture, not implementation. A `planned`, `stub`, or `research` row cannot be treated as supported merely because a CMake option, preset, or placeholder source file exists.

## CONVERGE-12 Final Enforcement Status

Strict validators are expected to pass:

- `python tools/validators/check_repo_layout.py --repo-root . --strict`
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`
- `python tools/validators/check_distribution_layout.py --repo-root . --strict`
- `python tools/validators/check_component_matrices.py --repo-root . --strict`

Repo and root allowlist strict modes pass with active explicit exceptions. Active exceptions are listed in `contracts/repo/layout_exceptions.toml` and summarized in `docs/repo/LAYOUT_EXCEPTION_LEDGER.md`.

Final audit: `docs/repo/audits/CONVERGE_12_FINAL_AUDIT.md`.
