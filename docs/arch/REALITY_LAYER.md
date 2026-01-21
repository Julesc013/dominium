# Reality Layer (REALITY0)

Status: binding.
Scope: canonical rules that determine what can be real, where, when, and under
whose authority.

The Reality Layer is the set of rules that determines what can be real, where,
when, and under whose authority. It is above execution, storage, and rendering,
and below gameplay rules (LIFE/CIV). It is independent of scale: macro and
micro representations obey the same reality rules.

## Reality Layer position
- Above: execution substrate (Work IR), storage (ECS), and rendering.
- Below: gameplay systems (LIFE/CIV and domain rules).
- Independent: scale, fidelity, and presentation.

## Glossary (short, canonical)
- ACT: authoritative simulation time; monotonic and immutable.
- Domain: explicit spatial volume that bounds where reality exists and laws apply.
- Existence State: explicit state of a subject (NONEXISTENT..ARCHIVED).
- Refinement: deterministic realization of micro state from macro state.
- Visitability: reachability plus refinable existence and a valid contract.
- Authority Layer: schema-defined band of power (simulation, temporal, spatial, etc.).
- Capability: additive permission to attempt an action.
- Law: gate that accepts/refuses/transforms intents and effects.
- Refusal: explicit, auditable denial with explanation.

## Canonical statement
Reality is explicit. A subject exists only in a declared existence state, inside
domains that define spatial legality, advancing on ACT, and operating under law
and capability gates. Refinement and visitability are contract-driven; absence,
refusal, and deferral are valid outcomes.

## Reality layer guarantees
- Existence is explicit; there is no implicit pop-in.
- Domains are first-class; there are no hidden world bounds.
- Travel is scheduled on ACT and never magical.
- Time perception is derived and never alters truth.
- Authority never bypasses law or archival history.
- Refinement is guaranteed by contract or denied deterministically.

## Existence and refinement
- Existence states are explicit and orthogonal to fidelity.
- Refinement is optional and contract-driven.
- Collapse preserves conservation, provenance, and observed history.
- Forking is the only valid way to alter archived history.

## Space and domains
- Domains are arbitrary 3D volumes; runtime representation is SDF.
- Authoring formats are baked/compiled deterministically into SDF.
- Domains may nest and overlap; precedence and jurisdiction are deterministic.
- Thin, irregular, and massive domains are all valid SDF volumes.
- Domains scale from rooms to galaxies without changing the model.
- All spatial permission checks go through domains; no other world bounds exist.
- Jurisdictions attach to domains, not implicit geography.

## Travel and reachability
- Travel is a graph of nodes and edges; movement is scheduled on ACT.
- Exotic travel is explicit edges with declared traversal semantics.
- Capacity, cost, and latency are mandatory for every edge.
- No teleportation without a declared edge.
- Travel may be queued, deferred, or refused deterministically.
- Reachable does not imply visitable.

## Visitability
- Arrival requires visitability checks (see the canonical contract).
- If a location cannot be refined, it must be unreachable.
- Placeholder or fake micro worlds are forbidden.

## Time and perception
- ACT is immutable; observer clocks derive perceived time.
- Dilation, buffering, and replay affect perception only.
- Different observers may see different time rates; truth remains identical.
- AI autorun worlds can advance via perception acceleration without warping ACT.
- Multiplayer consistency is preserved by ACT-based scheduling.

## Authority in reality
- No game modes exist; law + capability profiles define behavior.
- Spectator to god-mode is data configuration, not code paths.
- Omnipotence is additive capability, not bypass.
- All power flows through law-gated effects and audit trails.

## Reality flow (summary)
Intent -> law & capability gate -> reality checks -> scheduling (ACT) -> effect -> audit.
Refusal, absence, and deferral are valid outcomes.

## Scale and performance (non-executive)
- Macro-only civilizations can exist indefinitely.
- Refinement occurs only under interest and visitability.
- AI planning collapses to cohorts when appropriate.
- Domains bound computation and interest.
- Budgets and degradation are enforced via EXEC/HWCAPS interfaces.

## See also
- `docs/arch/LIFE_AND_POPULATION.md`
- `docs/arch/SPACE_TIME_EXISTENCE.md`
- `docs/arch/VISITABILITY_AND_REFINEMENT.md`
- `docs/arch/AUTHORITY_IN_REALITY.md`
- `docs/arch/REALITY_FLOW.md`
- `schema/existence/README.md`
- `schema/domain/README.md`
- `schema/travel/README.md`
- `schema/time/README.md`
- `schema/authority/README.md`
