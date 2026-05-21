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
