--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `launcher/`.

GAME:
- None. This spec is implemented under `launcher/`.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Launcher Packs (Pack / Mod / Runtime)

This spec defines the launcher pack ecosystem layer: a deterministic, instance-scoped pack graph described by TLV pack manifests and resolved into a stable load order.

Constraints:
- No UI involvement; works under `--ui=null --gfx=null`.
- No global pack state; enable/disable and policies are per-instance.
- All persistence is TLV (versioned, skip-unknown, forward-compatible).
- Deterministic behavior: same inputs produce the same resolved order and refusal reasons.

## 1. Pack manifest (`pack_manifest.tlv`)

`pack_manifest.tlv` is a versioned TLV container (skip-unknown; unknown fields are preserved and re-emitted unchanged when rewriting).

### 1.1 Root fields (schema version 1)

Required:
- `schema_version` (u32): `1`
- `pack_id` (string): stable identifier (lexicographic key)
- `pack_type` (u32): `content|mod|runtime`
- `version` (string): version identifier (compared deterministically; see 3.2)
- `pack_hash_bytes` (bytes): opaque pack hash metadata
- `compatible_engine_range` (container): version range
- `compatible_game_range` (container): version range

Dependencies (container, repeated):
- `required_dep`: dependency entry (id + version range)
- `optional_dep`: dependency entry (id + version range)
- `conflict`: dependency entry (id + version range)

Load order metadata (optional):
- `phase` (u32): `early|normal|late` (default `normal`)
- `explicit_order` (i32): default `0`

Feature flags:
- `capability` (string, repeated): declared capabilities (sorted for canonical encoding)
- `sim_flag` (string, repeated): simulation-affecting flags; must be declared as a capability

Declarative tasks (container, repeated):
- `install_task`
- `verify_task`
- `prelaunch_task`

### 1.2 Version range container

`version_range` is a container:
- `min` (string, optional): inclusive lower bound
- `max` (string, optional): inclusive upper bound

### 1.3 Dependency entry container

`dep_entry` is a container:
- `id` (string): required
- `range` (container): `version_range` (min/max may be empty)

### 1.4 Task container

Tasks are declarative and executed only via launcher services. Tasks may not mutate outside the instance root.

Supported kinds:
- `require_file`: requires a file to exist under the instance root (read-only check).

`task` is a container:
- `kind` (u32)
- `path` (string): instance-relative path; must not be absolute and must not escape via `..`.

### 1.5 Deterministic encoding

Canonical encoding rules:
- Known root tags are emitted in a fixed order.
- Repeated dependency lists and string lists are sorted deterministically before encoding.
- Unknown TLV records are preserved and re-emitted unchanged (root and nested containers).

## 2. Instance binding (instance-scoped pack state)

Packs are bound to an instance via `manifest.tlv` content entries (`type=pack|mod|runtime`):
- `enabled` (0/1): per-instance enable state
- `update_policy` (`never|prompt|auto`): per-instance policy
- `explicit_order_override` (i32, optional): per-instance load-order override used during resolution

There is no global enable/disable state. Dependency resolution operates only on enabled entries.

## 3. Dependency resolution (deterministic)

Resolution consumes the set of enabled pack-like entries in an instance manifest. Each enabled entry references an immutable artifact payload whose bytes are a `pack_manifest.tlv`.

### 3.1 Validation and strictness

For each enabled entry:
- The referenced payload must decode as a valid `pack_manifest.tlv`.
- Manifest identity must match the instance entry (`pack_id`, `version`, and `pack_type`).

Dependency rules:
- Required dependencies must be present as enabled instance entries and must satisfy the declared version range.
- Optional dependencies impose ordering only when present; if present they must satisfy the declared version range.
- Conflicts are enforced strictly: if a conflicting pack is present and its version is within the conflict range, resolution is refused.

All failures return explicit, deterministic reason strings (e.g., `missing_required_pack`, `required_version_mismatch`, `conflict_violation`, `cycle_detected`).

### 3.2 Version comparison

Version range comparisons are deterministic:
- If both versions parse as `MAJOR[.MINOR[.PATCH]]` with non-negative integers, they are compared numerically by `(major,minor,patch)`.
- Otherwise, versions are compared lexicographically as strings.
- Range bounds are inclusive.

### 3.3 Load order determinism

Resolved order is a topological sort over the dependency graph with deterministic tie-breaking.

Edges:
- For each dependency `A requires B`, add an edge `B -> A` (dependency loads before dependent).
- Optional dependencies add the same edge only when the optional pack is present.

Tie-break among nodes that are ready at the same time:
1. `phase` (`early` < `normal` < `late`)
2. effective order (`explicit_order_override` if present, else pack manifest `explicit_order`)
3. lexicographic `pack_id`

This yields a stable, deterministic order for the same input set.

## 4. Simulation safety model

Packs may declare simulation-affecting flags via `sim_flag`.

Rules:
- Any enabled pack with non-empty `sim_flag` must be pinned to an artifact payload (must have `hash_bytes` in the instance manifest entry).
- Launch is refused if dependency resolution fails (missing required packs, version mismatch, conflicts, cycles, or identity mismatches), ensuring sim-affecting packs cannot be implicitly missing or mismatched.
- Because instance manifest hashing includes content entries (including artifact hashes), enabled sim-affecting packs contribute to the instance manifest hash.

