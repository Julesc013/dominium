--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, deterministic scheduling primitives.
GAME:
- Market rules, matching policy, exchange contracts.
SCHEMA:
- Market and exchange record formats and validation constraints.
TOOLS:
- Inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No market as a source of goods.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_MARKETS_AND_EXCHANGE — Market Canon (CIV0+)

Status: draft
Version: 1

## Purpose
Define markets and exchange as mechanisms for matching supply and demand,
not sources of goods or value.

## Market (canonical)
Required fields:
- market_id (stable, unique within a timeline)
- domain_ref (spatial scope)
- exchange_rules (matching and pricing policy)
- currency_refs (allowed currencies or barter rules)
- participant_refs (eligible actors)
- provenance_refs (origin and causal chain)

Optional fields:
- settlement_ref (hosting settlement)
- institution_ref (regulating institution)
- access_policy_ref (admission rules)

## ExchangeContract (canonical)
Required fields:
- exchange_id
- offer_refs (declared supply)
- demand_refs (declared demand)
- settlement_terms (price, barter, or contract)
- schedule_policy (ACT-based timing)
- failure_modes (refuse, defer, partial)
- provenance_refs

## Rules (absolute)
- Markets do not create goods; they only exchange declared supply.
- All exchanges are scheduled on ACT.
- Market access may be absent or restricted; no global market assumption.

## Integration points
- Economic actors: `schema/economy/SPEC_ECONOMIC_ACTORS.md`
- Logistics: `schema/economy/SPEC_LOGISTICS.md`
- Governance: `schema/civ/SPEC_GOVERNANCE.md`
- Domains: `schema/domain/README.md`

## See also
- `docs/architecture/ECONOMY_AND_LOGISTICS.md`
