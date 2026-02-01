Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

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
# SPEC_ASSETS_INSTRUMENTS

Status: draft  
Version: 1

## Purpose
Define canonical asset definitions and instrument templates used by the ledger,
contracts, and markets. Assets and instruments are data-defined and deterministic.

## Scope
- Asset schemas (fungible and non-fungible).
- Instrument templates (contracts over assets and obligations).
- Provenance and conservation rules.

Out of scope:
- Money formatting and standards (see `docs/specs/SPEC_MONEY_STANDARDS.md`).
- Market clearing (see `docs/specs/SPEC_MARKETS.md`).

## Definitions
- Asset: A conserved unit of value or property identified by `asset_id`.
- Fungible asset: Units are interchangeable (e.g., wheat_unit).
- Non-fungible asset: Unique units with distinct identity (e.g., land_parcel_Y).
- Instrument: A contract template that creates obligations and schedules.

## Asset schema (conceptual)
Required fields:
- asset_id: stable hash or string ID.
- asset_kind: fungible | non_fungible.
- unit_scale: integer scale (e.g., 1, 100, 1000).
- divisibility: integer or enum (e.g., divisible, indivisible).
- provenance_required: bool.

Optional fields:
- issuer_id: entity or org issuing the asset.
- transfer_rules_id: reference to policy rules.
- display_name: non-sim metadata.
- tags: non-sim metadata.

Sim-affecting fields are explicitly enumerated and hashed.
Display names and tags are non-sim.

## Instrument template schema (conceptual)
Required fields:
- instrument_id: stable hash or string ID.
- instrument_kind: loan | bond | equity | option | future | lease | insurance | royalty.
- underlying_asset_ids: list of asset_id.
- obligation_template_id: reference to contract rules.
- schedule_template_id: reference to ACT-based schedules.
- settlement_rules_id: reference to deterministic settlement rules.

Optional fields:
- collateral_asset_ids.
- default_policy_id.
- jurisdiction_policy_id.

## Invariants
1. Assets are conserved and tracked by the ledger.
2. Instruments do not create assets; they create obligations and schedules.
3. All identifiers are stable and deterministic.
4. No implicit conversion between assets.

## Implementation notes (game layer)
- Assets and instruments are loaded from TLV packs into deterministic registries.
- Sim-affecting fields hashed for identity:
  - asset: id_hash, kind, unit_scale, divisibility, provenance_required, issuer_id_hash
  - instrument: id_hash, kind, contract_id_hash, asset_id_hash list (sorted)
- Non-sim metadata (display_name, tags) is excluded from sim digests.
- References are validated at load:
  - money standards must reference existing assets
  - instruments must reference existing contracts and assets

## Engine vs game responsibilities
ENGINE (Domino, C89/C90) MAY:
- implement asset ID hashing and serialization helpers.
- validate asset and instrument schema at load time.

ENGINE MUST NOT:
- encode asset names or real-world standards.
- interpret market or jurisdiction policy.

GAME (Dominium, C++98) MUST:
- load asset and instrument definitions from core data packs.
- bind instrument templates to contract implementations.
- enforce jurisdiction and governance policies.

## Examples
1) Fungible asset
- asset_id: wheat_unit
- unit_scale: 1
- divisibility: divisible
- provenance_required: true

2) Non-fungible asset
- asset_id: land_parcel_042
- unit_scale: 1
- divisibility: indivisible
- provenance_required: true

3) Bond instrument
- instrument_kind: bond
- underlying_asset_ids: [credit_unit]
- obligation_template: coupon_schedule + principal repayment

## Prohibitions
- Floating point units.
- Hard-coded real currency in engine.
- Instrument templates that mutate assets directly.
- Undocumented default conversions.

## Tests and validation requirements
Future tests MUST include:
- Asset schema validation (required fields, scale bounds).
- Instrument reference validation (all referenced assets exist).
- Deterministic ID hashing and ordering.

## Related specs
- `docs/specs/SPEC_LEDGER.md`
- `docs/specs/SPEC_CONTRACTS.md`
- `docs/specs/SPEC_MARKETS.md`
- `docs/specs/SPEC_MONEY_STANDARDS.md`
- `docs/specs/SPEC_PROVENANCE.md`