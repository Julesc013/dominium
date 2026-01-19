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
# SPEC_MONEY_STANDARDS

Status: draft  
Version: 1

## Purpose
Define money standards as renderers over base assets. A money standard does not
create value; it renders ledger amounts using deterministic rules.

## Scope
- Money standard schema and rules.
- Conversion and peg rules.
- Epistemic and governance integration.

Out of scope:
- Ledger implementation (see `docs/SPEC_LEDGER.md`).
- Market clearing (see `docs/SPEC_MARKETS.md`).

## Definitions
- Money standard: A renderer that expresses value in a named unit system.
- Base asset: The asset or basket the standard renders.
- Denomination: A subdivision or grouping for display and rounding.

## Money standard schema (conceptual)
Required fields:
- money_standard_id: stable hash or string ID.
- base_asset_id: asset used for value.
- denomination_scale: integer scale for display.
- rounding_mode: deterministic rule (floor, ceil, nearest).
- convertibility_rule_id: optional peg or basket reference.

Optional fields:
- locale_nameset_id (non-sim).
- legal_tender_rules_id (policy reference).
- display_name (non-sim).

Sim-affecting fields are explicitly enumerated and hashed.

## Rendering rules
1. Money standards are stateless renderers.
2. Rendering never mutates the ledger.
3. Conversion rules are explicit and deterministic.
4. Rounding rules are explicit and deterministic.

## Implementation notes (game layer)
- Standards load into a deterministic registry keyed by `id_hash`.
- Registry ordering is stable by `(id_hash, id_string)` for iteration and hashing.
- Sim-affecting fields hashed for identity:
  - id_hash
  - base_asset_id_hash
  - denom_scale
  - rounding_mode
  - convert_rule_id_hash
- Non-sim metadata (display_name, locale namesets) is excluded from sim digests.

## Resolution order
Standards are resolved by context (see `docs/SPEC_STANDARD_RESOLUTION.md`):
1. Explicit context
2. Organization standard
3. Jurisdiction standard
4. Personal preference
5. Fallback: numeric base asset value

No silent fallback. Conflicts must be visible.

## Epistemic gating
Actors can only use a money standard if they know it or have access to
required devices or documents. Unknown standards yield UNKNOWN renderings.

## Worked examples
1) Base asset rendering
- base_asset: credit_unit
- denomination_scale: 100
- 12345 -> "123.45" (deterministic rounding)

2) Pegged standard
- base_asset: credit_unit
- peg: 2 credit_unit per token
- rendering uses explicit peg rule at ACT time

3) Basket standard
- base_asset: basket of energy and food
- rendering uses fixed basket weights, no floating point

## Prohibitions
- Hard-coded real-world standards in engine.
- Implicit conversions.
- Floating point rounding.
- Locale or formatting logic in engine.

## Tests and validation requirements
Future tests MUST include:
- Deterministic rendering for the same ledger amount.
- Rounding rule determinism.
- Standard resolution order correctness.
- Unknown standard propagation.

## Related specs
- `docs/SPEC_LEDGER.md`
- `docs/SPEC_ASSETS_INSTRUMENTS.md`
- `docs/SPEC_STANDARD_RESOLUTION.md`
