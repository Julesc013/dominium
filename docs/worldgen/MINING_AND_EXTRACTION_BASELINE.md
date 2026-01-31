# Mining & Extraction Baseline (T9)

Status: baseline, deterministic, process-only.

This document defines the minimal mining and extraction layer that modifies
terrain via SDF overlays and produces visible material chunks without
introducing refining, crafting, or economy systems.

## What mining is (and is not)

Mining is a **process** that removes solid matter, updates resource density
fields, and emits physical material chunks. It is **not** a continuous
simulation and does not introduce production chains.

Included:
- Process-only cut (delta phi) overlays.
- Extraction that yields visible chunks plus tailings/waste.
- Deterministic depletion of resource density fields.
- Support checks that can trigger collapse fill overlays.

Excluded (explicitly):
- Refining, smelting, or crafting.
- Economy, ownership, or trade systems.
- Per-tick excavation or erosion.

## Process model

Mining is implemented by three deterministic processes:

- `process.mine.cut`
  - Writes a `delta_phi` overlay using a bounded tool radius.
  - Shape is deterministic and budget-limited.

- `process.mine.extract`
  - Samples geology/resource fields at the cut site.
  - Emits material chunks (assemblies) and tailings/waste.
  - Reduces `resource.density.*` fields deterministically.

- `process.mine.support_check`
  - Evaluates derived stress vs `support_capacity`.
  - Schedules collapse fill overlays when unstable.

All three processes obey law/meta-law and return explicit refusal reasons.

## Terrain modification

Mining modifies terrain through **SDF overlays**:

- Cut = subtraction (delta phi).
- Collapse fill = union (delta phi).

Overlays are:
- Process-generated only.
- Sparse and bounded.
- Deterministic and auditable.

## Material chunks

Extraction creates physical chunks with:
- `material_id`
- `mass`
- `volume`
- `purity`
- provenance

Chunks are **visible**, **movable**, and **persistent**. They do not
auto-stack or auto-convert into abstract resources.

## Depletion & run-out

Extraction reduces `resource.density.*` deterministically inside the mined
region. If a resource is depleted:
- Extraction yields tailings/waste only.
- The result explains the depletion state.

## Collapse & safety

Support checks compare derived stress to `support_capacity`:
- If stress > capacity, collapse is scheduled.
- Collapse fills voids with rubble via delta phi overlays.

No special tunnel-collapse code paths exist; collapse is a process outcome.

## Determinism & budgets

All mining operations:
- Use named RNG streams.
- Consume explicit budgets.
- Avoid per-tick scanning.
- Remain constant-cost with respect to world size.

## Maturity

This baseline is **BOUNDED**:
- It is intentionally coarse and deterministic.
- It is extensible via additional overlay types, richer chunk models,
  and higher-fidelity stress evaluation.
