# TOOLCHAIN Matrix Baseline

## Environments

- `linux-gcc-x86_64-arch`
- `linux-gcc-x86_64-debian13`
- `linux-gcc-x86_64-fedora`
- `macosx-clang-x86_64-10_14`
- `macosx-clang-x86_64-10_6`
- `win7-msvc-x86_64`
- `win8_1-msvc-x86_64`
- `winnt-msvc-x86_64-vs2026`
- `winxp-msvc-x86_32-legacy`

## Required Tests

- `toolchain.determinism_core`: `smoke.build_ids, smoke.endpoint_descriptors, smoke.release_manifest, determinism_core.worldgen_lock, determinism_core.baseline_universe`
- `toolchain.ecosystem`: `smoke.build_ids, smoke.endpoint_descriptors, smoke.release_manifest, determinism_core.worldgen_lock, determinism_core.baseline_universe, ecosystem.pack_verify, ecosystem.negotiation_smoke`
- `toolchain.full`: `smoke.build_ids, smoke.endpoint_descriptors, smoke.release_manifest, determinism_core.worldgen_lock, determinism_core.baseline_universe, ecosystem.pack_verify, ecosystem.negotiation_smoke, distribution.release_manifest_verify, heavy.convergence_gate`
- `toolchain.smoke`: `smoke.build_ids, smoke.endpoint_descriptors, smoke.release_manifest`

## Collection Method

- Run directory: `artifacts/toolchain_runs/winnt-msvc-x86_64-vs2026/run.5ea8970d1739f5c2`
- Run id: `run.5ea8970d1739f5c2`
- Source identity kind: `snapshot`
- Source snapshot hash: `f9301c8fbec955ed3632b6d6281bbd7349656c0e789aaf2087ead8ff355d47e8`
- Git revision hint: `01b6cf41e2618b9871594f3cb7b5932a2aa92316`
- Result: `complete`

## Current Reference Hashes

- Build ids hash: `990ece10acb2297ed355464f1d9237829ebabe27aff4b85a8ae91af3c46bc080`
- Endpoint semantic hash: `6bc74637c1b78059e57ce6a764c379381af82da41cccb66889efa1f73aaa692a`
- Worldgen snapshot hash: `608157d9bc07e76d9ee12546e76f255464c8dcc998a899d272cc848be649640e`
- Baseline universe hash: `1e4aca8f87ad76042c8c995b1dc9efb7871cc21e69d4e875b41750eef827b890`
- Gameplay snapshot hash: `86d64e4c8937301d037aeaf3d38200192216b70a2e7f10785d548a614e245fef`

## Comparison Method

- Compare `run_manifest.json`, `results.json`, and `hashes.json` from two run directories.
- Identical inputs require identical build ids.
- Same-environment comparisons require identical endpoint descriptor semantic hashes.
- Worldgen, baseline universe, gameplay, and proof anchor hashes are always blocking if they drift.

## Readiness

- Ω-9 surfaces exist and one committed reference run is archived for deterministic comparison.
- Additional environments can be populated later without expanding Tier 1 commitments.
- Ready for Ω-10 distribution-plan integration.
