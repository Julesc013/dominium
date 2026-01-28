# Economy and Logistics (CIV0+)

Status: binding.
Scope: canonical economy and logistics model for CIV0+.

Economy is conserved flow: inputs become outputs through explicit production
contracts. Logistics is scheduled movement of goods along Travel edges. There
is no global market and no instant supply chain.

## Economy as conserved flow
- Goods and services exist only if produced or extracted.
- Production requires inputs, time, and capacity.
- Consumption and decay are explicit effects.
- Actors cannot conjure value.

## Production chains
Production is defined by contracts with:
- inputs (resources, labor, time)
- outputs (goods, services)
- capacity limits
- failure modes (refuse or defer)
- ACT-based scheduling

## Markets and exchange
Markets are mechanisms, not sources of goods:
- exchange only declared supply and demand
- may be absent, local, or restricted
- pricing is policy, not magic

## Logistics
Logistics moves goods through the Travel graph:
- all movement is scheduled on ACT
- capacity and cost apply to every shipment
- delays, loss, and inspection are explicit

## Macro to micro consistency
Macro totals (production, trade, inventory) must reconcile with micro details
when refined. Refinement cannot invent goods to satisfy UI or balance.

## Invariants
- No goods without production inputs.
- No production without explicit contracts.
- No logistics bypasses the Travel graph.

## Dependencies
- Civilization model: `docs/arch/CIVILIZATION_MODEL.md`
- Travel and movement: `docs/arch/TRAVEL_AND_MOVEMENT.md`
- Reality layer: `docs/arch/REALITY_LAYER.md`
- Resource conservation: `schema/economy/SPEC_RESOURCE_CONSERVATION.md`

## Forbidden assumptions
- Markets create goods or value.
- Supply chains are instantaneous or global by default.

## See also
- `schema/economy/README.md`
