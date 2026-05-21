Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Result: PASS_WITH_WARNINGS

# MATRIX_CLEANUP_00

## Scope

`MATRIX-CLEANUP-00` normalized renderer, platform, native shell, support-tier,
and toolchain matrix vocabulary after `PORTABILITY-ARCH-POLICY-02`.

This was governance and documentation work only. It did not implement renderer
backends, native GUI, provider runtime, package runtime, workspace runtime,
runtime module loading, gameplay, or release publication.

## Relevant Invariants

- `AGENTS.md`: extend over replace, no silent support promotion, and honest
  validation reporting.
- `contracts/release/component_matrix.contract.toml`: matrix rows are planning
  contracts, not implementation claims.
- `contracts/build/floors.toml`: C17/C++17 and native platform floors constrain
  first-wave renderer/platform vocabulary.
- `docs/release/COMPONENT_MATRIX.md`: public prose mirror of matrix state.

## Changed Artifacts

- `.aide/context/latest-task-packet.md`
- `contracts/build/floors.toml`
- `contracts/release/component_matrix.contract.toml`
- `docs/architecture/RENDERER_RESPONSIBILITY.md`
- `docs/release/COMPONENT_MATRIX.md`
- `docs/release/NATIVE_APP_MATRIX.md`
- `docs/release/PLATFORM_MATRIX.md`
- `docs/release/RENDER_BACKEND_MATRIX.md`
- `docs/release/SUPPORT_TIERS.md`
- `docs/release/TOOLCHAIN_MATRIX.md`
- `docs/runtime/render/BACKENDS.md`
- `docs/runtime/render/PLATFORM_AND_BACKENDS.md`
- `docs/runtime/render/RENDER_INTERFACE.md`

## Matrix Decisions

- `soft` is now a transitional alias for the `software` renderer family.
- OpenGL renderer identity is the `opengl` family, with OpenGL 3.3-style shader
  architecture as the first-wave planned hardware target.
- OpenGL 2.1 and OpenGL 1.1 are back-port/research lanes, not first-wave
  architecture drivers.
- Direct3D renderer identity is the `direct3d` family, with Direct3D 11 as the
  first-wave Windows hardware target.
- Direct3D 9 is a back-port/research lane.
- Direct3D 12, Metal, and Vulkan are advanced/later lanes.
- `vk1` is a transitional alias for the `vulkan` family.
- `vector2d` is a transitional alias for the renderer-independent canvas drawing
  layer, not a renderer backend identity.
- Win32, Cocoa/AppKit, X11, and Wayland remain matrix-governed native shell or
  platform families; WinUI, SwiftUI, Qt, Android, and other non-floor targets
  remain research/advanced/optional lanes.

## Contract And Schema Impact

Matrix contract meaning changed by normalizing IDs and support phases. No schema
identity changed, and no runtime support was promoted without evidence.

## Evidence

`MATRIX-CLEANUP-00` landed as commit `64c1558a7`.

Later integrated coordinator proof from commit `bdfbe029e` reported:

- RepoX STRICT -> PASS with existing stale AuditX warning
- fast strict -> PASS, `33` commands, `305.687` seconds
- CMake configure/build and smoke CTest -> PASS through fast strict
- `git diff --check` -> PASS

Queue reconciliation reran focused validators after both commits; see
`docs/repo/audits/QUEUE_RECONCILE_00.md`.

## Non-Goals Preserved

- no renderer backend implementation
- no native GUI implementation
- no Workbench shell implementation
- no workspace runtime implementation
- no runtime module loader
- no provider runtime
- no package runtime
- no gameplay
- no release publication

## 2026-05-22 Rerun And Validator Hardening Addendum

This addendum records the MATRIX-CLEANUP-00 rerun after `WORKBENCH-VALIDATION-SLICE-01`
landed as `821bce25e`. A concurrent composition/lock task left additional
unstaged changes outside this task scope; those paths were not staged for this
matrix cleanup.

### Current Old IDs Found

- Renderer aliases or old identities: `gl1`, `gl2`, `gl4`, `dx9`, `dx11`,
  `dx12`, `vk1`, `soft`, and `vector2d`.
- Platform/tooling/history terms: `winui`, `swiftui`, `carbon`, `win16`,
  `freestanding_16bit`, `legacy_vc6`, `portable_zip`,
  `early_modern_desktop`, `broad_compatibility`, `retro_research`, and
  `advanced_modern`.

### Current Classification

- First-wave renderer families: `null`, `software`, `opengl`, and `direct3d`.
- First OpenGL hardware target: OpenGL 3.3 core, recorded as fields on the
  `opengl` family rather than as `gl4`.
- First Windows hardware target: Direct3D 11, recorded as fields on the
  `direct3d` family rather than as `dx11`.
- Later advanced renderer lanes: `metal`, `vulkan`, and Direct3D 12.
- Research/back-port lanes retained: OpenGL 2.1, OpenGL 1.1, and Direct3D 9.
- Renderer-independent drawing/canvas capability: `drawing.canvas`, with
  `vector2d` retained only as a transitional alias.

### Updated Artifacts

- `contracts/release/component_matrix.contract.toml`
- `contracts/platform/renderer_portability.matrix.json`
- `contracts/platform/platform_floor.registry.json`
- `contracts/platform/product_mode_portability.matrix.json`
- `contracts/platform/package_portability.matrix.json`
- `docs/release/COMPONENT_MATRIX.md`
- `docs/release/RENDER_BACKEND_MATRIX.md`
- `docs/architecture/RENDERER_RESPONSIBILITY.md`
- `docs/build/CI_MATRIX.md`
- `docs/build/PRESET_NAMING.md`
- `docs/development/guides/BUILDING.md`
- derived historical development guides under `docs/development/guides/`
- `tools/validators/check_component_matrices.py`
- `tests/contract/component_matrix/fixtures/`

### Validator Hardening

`tools/validators/check_component_matrices.py` now rejects version-coded or
capability-coded renderer identities as top-level first-wave renderer families,
requires first-wave role fields for preferred renderer families, requires
OpenGL 3.3/profile and Direct3D 11 fields for the first hardware targets, and
checks component-matrix fixtures for valid and invalid renderer-policy cases.

### Contract And Schema Impact

Contract data and validator expectations changed. No schema identity changed,
and no renderer/platform/provider/runtime support was promoted without
provider/conformance proof.

### Validation

- `python tools/validators/check_component_matrices.py --repo-root . --strict`
  -> PASS, fixtures checked `6`, valid `2`, invalid `4`.
- `python tools/validators/platform/check_portability_matrix.py --repo-root . --strict`
  -> PASS.
- `python tools/validators/platform/check_portability_matrix.py --repo-root . --fixtures`
  -> PASS.
- `python tools/validators/contracts/check_provider_model.py --repo-root . --strict`
  -> PASS.
- `python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict`
  -> PASS.
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
  -> PASS.
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict`
  -> PASS with `68` existing warnings and `0` violations.
- `python scripts/verify_docs_sanity.py --repo-root .` -> PASS.
- `python scripts/verify_build_target_boundaries.py --repo-root .` -> PASS.
- `python scripts/verify_ui_shell_purity.py --repo-root .` -> PASS.
- `python scripts/verify_abi_boundaries.py --repo-root .` -> PASS.
- `py -3 .aide/scripts/aide_lite.py doctor` -> PASS.
- `py -3 .aide/scripts/aide_lite.py validate` -> PASS with existing review
  packet reference warnings.
- `git diff --check` -> PASS.
- `python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/MATRIX-CLEANUP-00-fast-strict.json --md-out .aide/reports/MATRIX-CLEANUP-00-fast-strict.md`
  -> PASS, `33` commands, `369.954` seconds.

### Remaining Warnings

- Dependency-direction strict still reports the known `68` warning-class
  dependency findings and `0` violations.
- AIDE validate still reports existing review packet reference warnings.
- Full CTest remains outside this task and remains T4/full-gate debt.

### Next

Proceed to `WORKBENCH-VALIDATION-SLICE-01` only if the coordinator still wants
that historical next step. In the current queue state after `821bce25e`, the
active next packet has moved beyond this matrix cleanup.
