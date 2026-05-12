# Post-CONVERGE Next Steps

Status: PROVISIONAL

Phase: POST-CONVERGE

## Immediate Correction After POST-CONVERGE-00

POST-CONVERGE-00 confirmed that exception retirement and build/runtime proof must precede platform, render, native shell, worldgen, and broad domain expansion.

Current priority order:

1. exception triage
2. generated/output cleanup
3. build/FAST remediation
4. canonical local runtime/playtest proof

Planning references:

- `docs/repo/audits/POST_CONVERGE_00_HEALTH.md`
- `docs/repo/audits/POST_CONVERGE_EXCEPTION_TRIAGE.md`
- `docs/repo/EXCEPTION_RETIREMENT_QUEUE.md`
- `docs/repo/BUILD_ENVIRONMENT_REMEDIATION.md`

## What Can Proceed

The repository is ready for scoped work in these areas:

- platform host work
- renderer backend work
- native OEM+ setup/launcher shells
- AppShell enforcement refinement
- worldgen and domain realism work
- release and package work

Each area must use the current authority stack and matrix status rather than older path claims.

## What Must Not Happen

- no new root-level domain folders
- no new root-level product folders
- no GUI toolkit owning product semantics
- no renderer owning simulation truth
- no distribution/runtime/install/media roots treated as source roots
- no support claims without component matrix status
- no new machine-readable authority under transitional roots without contract review

## Suggested Sequence

1. AppShell/product mode enforcement
2. null/software runtime baseline verification
3. platform host proof: Win32, POSIX, Cocoa, X11, Wayland
4. render backend proof: OpenGL compatibility, D3D11, Metal, Vulkan
5. native setup/launcher/admin shells
6. worldgen/domain realism expansion through contracts/game/content/docs/tests split

## Domain Work Rule

Future domain work must use the split model:

- schemas, registries, capabilities, and protocols under `contracts/`
- implementation under `game/domains/`
- authored data and packs under `content/`
- human explanation under `docs/domains/`
- fixtures, determinism, regression, and golden tests under `tests/`

## Matrix Rule

Future platform/render/native/toolchain/package work must update `contracts/release/component_matrix.contract.toml` and relevant `docs/release/*_MATRIX.md` docs when status changes.

Planned, stub, and research rows are not supported implementations.
