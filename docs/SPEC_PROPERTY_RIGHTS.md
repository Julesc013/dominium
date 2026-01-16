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
# SPEC_PROPERTY_RIGHTS

Status: draft  
Version: 1

## Purpose
Define property rights as non-fungible assets with explicit usage contracts.
Property rights are governed, transferable, and auditable.

## Scope
- Property right schema.
- Ownership, encumbrances, and transfer rules.
- Integration with ledger and contracts.

## Definitions
- Property right: A non-fungible asset that grants defined usage or control.
- Encumbrance: A contract or claim that limits usage or transfer.
- Title: The authoritative ownership record for a property right.

## Schema (conceptual)
Required fields:
- property_id: stable hash or string ID.
- asset_id: non-fungible asset backing the right.
- owner_id: current owner.
- jurisdiction_policy_id: applicable governance rules.
- usage_contract_ids: contracts that define allowed usage.

Optional fields:
- encumbrance_ids: liens, easements, leases.
- provenance_id: origin record.

## Rules
1. Transfers are explicit ledger events and contract updates.
2. Encumbrances remain attached across transfers unless released.
3. Property rights are not created without construction provenance.
4. Ownership changes are auditable and deterministic.

## Worked examples
1) Land parcel with lease
- property_id: land_parcel_042
- encumbrance: lease contract for tenant access

2) Factory building
- property right backed by construction provenance
- usage contract limits production type

## Prohibitions
- Implicit ownership changes.
- Silent removal of encumbrances.
- Property creation without provenance.

## Tests and validation requirements
Future tests MUST include:
- Ownership transfer determinism.
- Encumbrance persistence across transfers.
- Provenance trace validation.

## Related specs
- `docs/SPEC_LEDGER.md`
- `docs/SPEC_CONTRACTS.md`
- `docs/SPEC_PROVENANCE.md`
