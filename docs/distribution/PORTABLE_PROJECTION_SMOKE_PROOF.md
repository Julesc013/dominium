# Portable Projection Smoke Proof

## Status

- Phase: POST-CONVERGE-09
- Status: partial
- Date: 2026-05-12

## Purpose

This document records local portable projection smoke evidence. It is not public release support, installer proof, package signing proof, media proof, or a change to distribution semantics.

## Inputs

| Input | Status | Notes |
| --- | --- | --- |
| build path | blocked | `cmake --preset verify` still requires a local Visual Studio 17 2022 generator instance |
| product boot proof | partial | POST-CONVERGE-08 proved script/wrapper help surfaces only; no native product binaries |
| distribution contract | present | `contracts/distribution/layout.contract.toml` declares `portable_install` and `package_export` projections |
| package/export docs | present | portable install, package export, cache/staging, bundle/diagnostic, and packaging matrix docs exist |
| setup/package/projection commands | partial | package tooling and packaging pipeline help surfaces exist; assemble/portable generation requires build outputs |

## Expected Portable Projection Layout

Required manifests:

- `install.manifest.json`
- `semantic_contract_registry.json`
- `release.manifest.json`

Required roots:

- `bin/`
- `descriptors/`
- `store/packs/`
- `store/profiles/`
- `store/locks/`
- `instances/`
- `saves/`
- `exports/`
- `logs/`
- `runtime/ipc/`
- `runtime/locks/`
- `runtime/temp/`
- `cache/`
- `ops/transactions/`
- `docs/`
- `LICENSES/`

## Smoke Command Sequence

| Status | Purpose | Command | Expected Result | Output Path |
| --- | --- | --- | --- | --- |
| blocked | configure canonical verify lane | `cmake --preset verify` | configure succeeds | `out/build/vs2026/verify/` |
| blocked | build product binaries | `cmake --build --preset verify` | native product binaries produced | `out/build/vs2026/verify/bin/` |
| blocked | assemble artifact root | `python apps/setup/packages/scripts/packaging/pipeline.py assemble --build-dir out/build/vs2026/verify --out <temp>/artifact_root --version 0.0.0-smoke` | artifact root produced from build outputs | temp only |
| blocked | create portable archive | `python apps/setup/packages/scripts/packaging/pipeline.py portable --artifact <temp>/artifact_root --out <temp>/portable --version 0.0.0-smoke` | portable archive generated | temp only |
| partial | audit projection contract and commands | `python tools/validators/check_portable_projection.py --repo-root . --dry-run` | expected layout and command sequence printed | none |
| partial | smoke `.dompkg` pack/verify toolchain | `python tools/distribution/tool_pkg_pack.py ...` then `python tools/distribution/tool_pkg_verify.py --pkg <temp>/smoke_docs.dompkg` | temporary docs package packs and verifies | temp output removed |

## Actual Result

| Check | Result | Notes |
| --- | --- | --- |
| projection generated? | no | build output is missing, so artifact assembly is blocked |
| projection validated? | no | no real projection root exists to validate |
| manifests present? | no | no generated portable root exists |
| binaries present? | no | no native product binaries exist locally |
| required roots present? | not applicable | dry-run validator lists expected roots only |
| `.dompkg` smoke artifact generated? | yes, temporary | a one-file docs smoke package was created under `%TEMP%`, verified, and removed |
| generated output committed? | no | no package or projection output is committed |

## Current Blockers

- Local `cmake --preset verify` cannot configure because Visual Studio 17 2022 is missing.
- No build output exists for `setup`, `launcher`, `client`, `server`, or `tools`.
- The packaging pipeline `assemble` command requires a build directory containing built outputs.
- No current command was proven to generate `install.manifest.json`, `semantic_contract_registry.json`, and `release.manifest.json` into a portable root.
- Product boot proof remains partial and does not prove native binaries for `bin/`.
- Setup Python bridge and `dist/bin/dom` blockers remain from POST-CONVERGE-08.

## Non-Goals

- No public release.
- No package signing proof.
- No installer proof.
- No media layout proof.
- No runtime feature work.
