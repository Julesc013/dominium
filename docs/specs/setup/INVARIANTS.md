# Setup Invariants

## Architecture Layers
- Layer 0: Setup Kernel (pure orchestration, deterministic, no side effects)
- Layer 1: Runtime Services (all side effects behind facades)
- Layer 2: Frontends / Adapters (UI, CLI, MSI, PKG, deb/rpm, Steam)

## Hard Prohibitions
- Kernel may not include OS headers.
- Kernel may not touch filesystem, registry, network, or processes.
- Frontends may not implement install logic.
- All contracts are TLV.
- All planning is deterministic.
- All installs are resumable.
- No in-place mutation of live installs.

## Required Properties
- Deterministic selection.
- Auditable decisions.
- Stable error taxonomy.
- Atomic transactions (stage → verify → commit).
- Crash recovery (resume or rollback).
