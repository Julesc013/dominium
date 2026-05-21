Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Architecture Targets

Dominium build governance recognizes architecture tiers. It does not add platform support claims from build presets alone.

## Mainline

The mainline full native product tier is `source_native_64`:

```text
x86_64
arm64
64-bit word size
little endian
C17/C++17
C-compatible public ABI
```

Existing `x64` matrix rows are compatibility aliases for `x86_64`.

## Constrained And Projection Lanes

`constrained_native_32` may be used for explicitly limited 32-bit work. It is not a requirement that every provider, renderer, product mode, Workbench surface, or tool work there.

`contract_projection` and `archive_runner` are compatibility lanes for viewers, snapshots, generated subsets, archive replay, emulation, or research. They are not full native products.

## Build Evidence

A build can prove only what its row says it proves. Full native product support additionally needs smoke, product, package, and release evidence. Release generation and CI expansion are outside the architecture policy task.

Use the portability and architecture validators together:

```text
python tools/validators/platform/check_architecture_policy.py --repo-root . --strict
python tools/validators/platform/check_portability_matrix.py --repo-root . --strict
```
