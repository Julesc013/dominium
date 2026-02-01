Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# SPEC_CAPABILITIES — SIM_CAPS vs PERF_CAPS

This spec defines the capability split used for compatibility, identity
digests, and QoS negotiation.

## 1. Scope
- SIM_CAPS are authoritative and sim-affecting.
- PERF_CAPS are negotiable and non-sim.
- SIM_CAPS MUST be present in launcher handshakes.
- PERF_CAPS MAY be present and may change over time.

## 2. SIM_CAPS (authoritative)
SIM_CAPS define deterministic compatibility and are pinned in identity digests.

Required fields (versioned TLV):
- `determinism_grade` (u32)
- `math_profile` (u32; fixed-point profile ID)
- `sim_flags` (u32; sim-affecting flags, if any)

Rules:
- SIM_CAPS MUST be validated against the required baseline at load time.
- Any SIM_CAPS mismatch MUST refuse or require migration.
- SIM_CAPS are included in the handshake identity digest.

## 3. PERF_CAPS (non-sim)
PERF_CAPS describe throughput/presentation characteristics only.

Required fields (versioned TLV):
- `tier_profile` (u32; see `docs/specs/SPEC_TIERS.md`)
- `perf_flags` (u32)

Rules:
- PERF_CAPS MUST NOT influence authoritative simulation.
- PERF_CAPS are excluded from identity digests.
- PERF_CAPS may be negotiated via QoS/assistance.

## 4. Hashing and identity digest
Canonical hashes:
- `sim_caps_hash64` is computed from the canonical SIM_CAPS TLV.
- `perf_caps_hash64` is computed from the canonical PERF_CAPS TLV (logging only).

Handshake identity digest MUST include:
- `sim_caps_hash64`
- content digest(s)
- provider bindings digest
- sim-affecting flags (included in SIM_CAPS TLV)

PERF_CAPS MUST NOT influence the identity digest.

## 5. Compatibility policy
- SIM_CAPS version or field mismatches require migration or refusal.
- PERF_CAPS mismatches only affect presentation/throughput policy.

## Related specs
- `docs/specs/SPEC_TIERS.md`
- `docs/specs/launcher/SPEC_LAUNCH_HANDSHAKE_GAME.md`
- `docs/specs/SPEC_QOS_ASSISTANCE.md`
- `docs/specs/SPEC_DETERMINISM.md`
- `docs/specs/SPEC_FEATURE_EPOCH.md`