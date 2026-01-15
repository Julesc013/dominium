# Launcher Core (Foundation)

## Responsibilities

The launcher core is a **deterministic instance manager** with **zero UI assumptions**.
It owns a pure state model for:

- **Instances** (and their lockfile manifests)
- **Profiles** (launcher policy + allowed backends)
- **Artifacts** (opaque references only)
- **Tasks** (install/verify/launch lifecycle as explicit state transitions)
- **Runs / audits** (every execution records *selected-and-why*)

All side effects (filesystem, networking, process spawn, hashing, archive extraction, time) flow through the **versioned C ABI** facade in `source/dominium/launcher/core/include/launcher_core_api.h`.

## Determinism Guarantees

- Reducers are **side-effect free** and depend only on explicit inputs.
- Persistence is **TLV**, **versioned at the root**, **skip-unknown**, and designed for future migrations.
- Every run emits an audit record; **no silent decisions**.

## Audit Output

- `launcher_core_emit_audit()` persists a TLV file.
- If `audit_output_path` is NULL, the core writes `launcher_audit_<runid_hex>.tlv` in the current working directory.

## Instance Lifecycle (Core View)

1. Load/select a profile (or use the null profile).
2. Create/load an instance manifest (lockfile) with explicit ordering and pins.
3. Schedule tasks (install/verify/launch) as explicit transitions.
4. Emit an audit TLV recording inputs, selections, reasons, and outcome.

## TLV Schemas

Implemented schemas:

- **Launcher Profile TLV**: id, allowed backends, policy flags, determinism constraints
- **Instance Manifest TLV**: instance id, pinned build ids, pinned content/mod list + hashes + ordering, update policies, known-good marker
- **Audit Log TLV**: run id, timestamp, selected profile/backends, reasons, versions/hashes, exit result

Migration hooks are defined but not implemented in this foundation.
