# TOOLCHAIN-MATRIX-0

## A) Environments

Each environment records:

- `env_id`
- `os_id`
- `arch_id`
- `abi_id`
- `compiler_id` + `compiler_version`
- `toolchain_constraints`
- `stability_class = provisional`
- canonical target/platform bindings in `extensions`

Planned environment ids:

- `linux-gcc-x86_64-arch`: linux / x86_64 / glibc / gcc 14
- `linux-gcc-x86_64-debian13`: linux / x86_64 / glibc / gcc 14
- `linux-gcc-x86_64-fedora`: linux / x86_64 / glibc / gcc 14
- `macosx-clang-x86_64-10_14`: macosx / x86_64 / cocoa / clang 12
- `macosx-clang-x86_64-10_6`: macosx / x86_64 / cocoa / clang legacy
- `win7-msvc-x86_64`: win7 / x86_64 / msvc / msvc 2019+
- `win8_1-msvc-x86_64`: win8_1 / x86_64 / msvc / msvc 2022+
- `winnt-msvc-x86_64-vs2026`: winnt / x86_64 / msvc / msvc 2026
- `winxp-msvc-x86_32-legacy`: winxp / x86_32 / msvc / msvc legacy

## B) Required Tests Per Environment

- `toolchain.smoke`: build ids, endpoint descriptors, release manifest generation when dist exists
- `toolchain.determinism_core`: smoke + worldgen lock verify + baseline universe verify
- `toolchain.ecosystem`: determinism-core + pack verify + negotiation handshake smoke
- `toolchain.full`: ecosystem + dist verify when packaging exists + optional convergence gate

Profile definitions:

- `toolchain.determinism_core`: Smoke tests plus WORLDGEN-LOCK and BASELINE-UNIVERSE short-window verification.
- `toolchain.ecosystem`: Determinism-core plus deterministic pack verification and negotiation handshake smoke.
- `toolchain.full`: Ecosystem coverage plus dist verification when packaging exists and optional heavy convergence replay.
- `toolchain.smoke`: Build identity and descriptor emission for an environment, with release-manifest generation when a dist root exists.

## C) Output Artifacts

Each run writes canonical JSON under `artifacts/toolchain_runs/<env_id>/<run_id>/`:

- `run_manifest.json`
- `results.json`
- `env_report.json`
- `hashes.json`
- `build_ids.json`
- `endpoint_descriptors.json`

Canonical output hashes include:

- build-id list hash
- endpoint descriptor hash set
- endpoint descriptor semantic hash set
- worldgen snapshot hash
- baseline universe hash
- gameplay snapshot hash
- proof anchor hashes

## Acceptance Rules

- `run_id = hash(env_descriptor + profile_descriptor + git_revision_or_source_snapshot_hash)`
- If inputs are identical, build ids MUST match.
- For same-`env_id` comparisons, endpoint descriptor semantic hashes MUST match.
- Worldgen, baseline universe, gameplay, and proof anchor hashes MUST match across all toolchain runs.
- Dist verification and convergence are optional when their prerequisites are absent.
