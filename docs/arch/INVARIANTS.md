# Invariants (CANON0)

Status: binding.
Scope: hard invariants for all systems, documentation, and data.

Canonical summary: this document.

Each invariant includes why it exists, what breaks if violated, and which
systems enforce it.

## Invariant: Deterministic authoritative simulation (batch == step)
Why:
- Reproducibility, auditability, and cross-platform agreement depend on it.
Breaks if violated:
- Replays diverge, cross-shard reconciliation fails, and saves become invalid.
Enforced by:
- Work IR + Access IR (`schema/execution/README.md`)
- `docs/arch/EXECUTION_REORDERING_POLICY.md`
- `docs/arch/DETERMINISTIC_REDUCTION_RULES.md`
- CI: EXEC0b-REORDER-001, EXEC0b-COMMIT-001

## Invariant: Simulation advances only via explicit events (no global scans)
Why:
- Event scheduling keeps costs bounded and deterministic.
Breaks if violated:
- Hidden background work, O(N) scans, and per-tick AI loops cause drift and
  unpredictable budgets.
Enforced by:
- ARCH0 A2 (`docs/arch/ARCH0_CONSTITUTION.md`)
- Event-driven scheduling specs (e.g., `docs/specs/SPEC_EVENT_DRIVEN_STEPPING.md`)
- Guides: `docs/guides/NO_GLOBAL_ITERATION_GUIDE.md`
- CI: CIV5-WAR3-NOGLOB-005, CIV5-WAR4-NOGLOB-004

## Invariant: ACT is monotonic and never warped
Why:
- ACT is the authoritative time axis for determinism and ordering.
Breaks if violated:
- Travel scheduling, replay, and law decisions become nondeterministic.
Enforced by:
- `docs/arch/TIME_DILATION_WITHOUT_TIME_WARP.md`
- `schema/time/README.md`
- CI: TIME2-NO-ACT-WARP-001

## Invariant: No implicit existence
Why:
- Existence must be auditable and lawful.
Breaks if violated:
- Pop-in creation, silent erasure, and unverifiable provenance.
Enforced by:
- `docs/arch/EXISTENCE_AND_REALITY.md`
- `schema/existence/README.md`
- CI: EXIST0-STATE-001, EXIST0-NOPOP-002

## Invariant: No refinement without a contract
Why:
- Refinement must be deterministic and provenance-preserving.
Breaks if violated:
- Fake worlds, fabricated history, and nondeterministic detail.
Enforced by:
- `docs/arch/REFINEMENT_CONTRACTS.md`
- `docs/arch/VISITABILITY_CONSISTENCY.md`
- CI: EXIST1-CONTRACT-001, DOMAIN4-NOFAKE-002

## Invariant: No teleport without a TravelEdge
Why:
- Movement must be schedulable, law-gated, and auditable.
Breaks if violated:
- Reachability lies, bypassed costs, and broken domain law.
Enforced by:
- `docs/arch/TRAVEL_AND_MOVEMENT.md`
- `docs/arch/NO_MAGIC_TELEPORTS.md`
- CI: TRAVEL0-NO-TELEPORT-001, TRAVEL2-NO-MAGIC-001

## Invariant: Reachability implies visitability
Why:
- If something can be reached, it must be real and refinable.
Breaks if violated:
- Players can arrive at non-real or non-refinable destinations.
Enforced by:
- `docs/arch/VISITABILITY_AND_REALITY.md`
- `schema/domain/SPEC_VISITABILITY.md`
- CI: DOMAIN4-VISIT-001, DOMAIN4-NOFAKE-002

## Invariant: No authority without capability and law
Why:
- Authority must be explicit, scoped, and auditable.
Breaks if violated:
- Hidden admin bypass, cheat-only paths, and unverifiable outcomes.
Enforced by:
- `docs/arch/AUTHORITY_AND_OMNIPOTENCE.md`
- `docs/arch/LAW_ENFORCEMENT_POINTS.md`
- `schema/authority/README.md`
- CI: OMNI0-NO-ISADMIN-001, OMNI0-NOBYPASS-003

## Invariant: Authority gates actions only, never visibility (AUTH3-AUTH-001)
Why:
- Visibility is epistemic; authority is action gating only.
Breaks if violated:
- Hidden enforcement, nondeterministic views, and un-auditable censorship.
Enforced by:
- `docs/arch/AUTHORITY_AND_ENTITLEMENTS.md`
- `docs/arch/DEMO_AND_TOURIST_MODEL.md`
- Tests: `tests/authority/`, `tests/tourist/`

## Invariant: Entitlements gate authority issuance only (AUTH3-ENT-002)
Why:
- Entitlements are platform-facing; engine/game must stay neutral.
Breaks if violated:
- Platform lock-in and hidden enforcement in simulation logic.
Enforced by:
- `docs/arch/DISTRIBUTION_AND_STOREFRONTS.md`
- Tests: `tests/entitlement/`

## Invariant: Demo is an authority profile, not a build (AUTH3-DEMO-003)
Why:
- One distribution prevents paywalled forks and drift.
Breaks if violated:
- Divergent code paths and inconsistent determinism.
Enforced by:
- `docs/arch/DISTRIBUTION_AND_STOREFRONTS.md`
- `docs/arch/DEMO_AND_TOURIST_MODEL.md`
- Tests: `tests/demo/`, `tests/distribution/`

## Invariant: Tourists never mutate authoritative state (AUTH3-TOURIST-004)
Why:
- Observation must not become hidden authority.
Breaks if violated:
- Untracked mutations and integrity drift.
Enforced by:
- `docs/arch/DEMO_AND_TOURIST_MODEL.md`
- Tests: `tests/tourist/`

## Invariant: Services affect access only (AUTH3-SERVICE-005)
Why:
- Services are optional and external to determinism.
Breaks if violated:
- Altered outcomes and invalidated replays.
Enforced by:
- `docs/arch/SERVICES_AND_PRODUCTS.md`
- Tests: `tests/services/`

## Invariant: Piracy contained by authority, not DRM (AUTH3-PIRACY-006)
Why:
- Copying is allowed; durable value is authority-bound.
Breaks if violated:
- Hidden penalties, degraded simulation, and non-archival behavior.
Enforced by:
- `docs/arch/PIRACY_CONTAINMENT.md`
- Tests: `tests/piracy_containment/`

## Invariant: Authority upgrades/downgrades do not mutate state (AUTH3-UPGRADE-007)
Why:
- Authority changes are administrative, not simulation events.
Breaks if violated:
- Hidden state mutation and replay divergence.
Enforced by:
- `docs/arch/UPGRADE_AND_CONVERSION.md`
- Tests: `tests/authority/`, `tests/services/`

## Invariant: Saves are tagged by authority scope (AUTH3-SAVE-008)
Why:
- Save provenance must remain explicit and auditable.
Breaks if violated:
- Silent promotion of non-authoritative saves.
Enforced by:
- `docs/arch/UPGRADE_AND_CONVERSION.md`
- Tests: `tests/authority/`

## Invariant: Control layers never interfere with authoritative simulation
Why:
- Control layers are optional and external; they must not change outcomes.
Breaks if violated:
- Replays diverge, archival verification fails, and law enforcement becomes
  untrustworthy.
Enforced by:
- `docs/arch/NON_INTERFERENCE.md`
- `docs/arch/CONTROL_LAYERS.md`
- Tests: `tests/control/interference/`

## Invariant: No secrets in engine or game
Why:
- Engine/game are portable, public, and replay-verifiable; secrets break trust.
Breaks if violated:
- Credential exposure, covert policy enforcement, and irreproducible builds.
Enforced by:
- `docs/arch/CONTROL_LAYERS.md`
- `docs/arch/THREAT_MODEL.md`
- Tests: `tests/control/audit/`

## Invariant: Refusal and absence are first-class outcomes
Why:
- Systems must fail deterministically and explainably.
Breaks if violated:
- Silent fallbacks, undefined behavior, or forced workarounds.
Enforced by:
- `docs/arch/REFUSAL_AND_EXPLANATION_MODEL.md`
- ARCH0 A7 (`docs/arch/ARCH0_CONSTITUTION.md`)
- CI: EXEC0-ABSENCE-001

## Invariant: Authoritative mutation only through Work IR + law gates
Why:
- Ensures auditability and enforcement consistency.
Breaks if violated:
- Untracked state changes and law bypass paths.
Enforced by:
- `docs/arch/EXECUTION_SUBSTRATE_AUDIT.md`
- `docs/arch/LAW_ENFORCEMENT_POINTS.md`
- CI: EXEC0-IR-001, EXEC0c-LAW-REQ-001

## Invariant: Deterministic reductions and commit ordering
Why:
- Parallelism must not change outcomes.
Breaks if violated:
- Nondeterministic totals, inconsistent ledgers, and diverging replicas.
Enforced by:
- `docs/arch/DETERMINISTIC_REDUCTION_RULES.md`
- `docs/arch/EXECUTION_REORDERING_POLICY.md`
- CI: EXEC0b-REDUCE-001, EXEC0b-COMMIT-001

## Invariant: Distribution and sharding are deterministic
Why:
- Cross-shard outcomes must be reproducible and auditable.
Breaks if violated:
- Divergent shard ownership, nondeterministic message ordering.
Enforced by:
- `schema/distribution/README.md`
- `docs/arch/DOMAIN_SHARDING_AND_STREAMING.md`
- CI: DOMAIN3-SHARD-001, CIV5-WAR4-SHARD-005

## Invariant: Archived history is immutable (fork to change it)
Why:
- Historical integrity and auditability depend on immutability.
Breaks if violated:
- Silent history edits and unverifiable replays.
Enforced by:
- `docs/arch/ARCHIVAL_AND_PERMANENCE.md`
- `docs/arch/TIMELINE_FORKS_AND_HISTORY.md`
- CI: EXIST2-FREEZE-001, EXIST2-FORK-002

## Invariant: Tools cannot bypass law (read-only by default)
Why:
- Tooling must not become a hidden admin channel.
Breaks if violated:
- Untracked mutations, integrity drift, and replay divergence.
Enforced by:
- `docs/arch/TOOLS_AS_CAPABILITIES.md`
- `schema/tools/README.md`
- CI: OMNI1-NOTOOLBYPASS-001, TOOL0-NOMUT-004

## Invariant: Scaling is a semantics-preserving projection (SCALE0-PROJECTION-001)
Why:
- Macro state must not contradict micro truth.
Breaks if violated:
- Expanding a domain changes outcomes or fabricates history.
Enforced by:
- `docs/arch/SCALING_MODEL.md`
- `docs/arch/COLLAPSE_EXPAND_CONTRACT.md`
- Tests: `tests/app/scale0_contract_tests.py`

## Invariant: Conservation across collapse/expand (SCALE0-CONSERVE-002)
Why:
- Totals and obligations must remain exact across fidelity tiers.
Breaks if violated:
- Resource/energy/population drift, broken contracts, authority inconsistencies.
Enforced by:
- `docs/arch/INVARIANTS_AND_TOLERANCES.md`
- `docs/arch/COLLAPSE_EXPAND_CONTRACT.md`
- Tests: `tests/app/scale0_contract_tests.py`

## Invariant: Collapse/expand only at commit boundaries (SCALE0-COMMIT-003)
Why:
- Commit boundaries are the only safe points for deterministic transitions.
Breaks if violated:
- Mid-commit state changes create nondeterministic outcomes.
Enforced by:
- `docs/arch/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/arch/EXECUTION_MODEL.md`
- Tests: `tests/app/scale0_contract_tests.py`

## Invariant: Deterministic macro time ordering (SCALE0-DETERMINISM-004)
Why:
- Cross-thread determinism and replay depend on stable ordering.
Breaks if violated:
- Divergent replays, shard disagreements, and audit failure.
Enforced by:
- `docs/arch/MACRO_TIME_MODEL.md`
- `docs/arch/EXECUTION_REORDERING_POLICY.md`
- Tests: `tests/app/scale0_contract_tests.py`

## Invariant: Sufficient statistics within declared tolerances (SCALE0-TOLERANCE-005)
Why:
- Bounded approximation prevents drift and invalid refinements.
Breaks if violated:
- Unbounded error accumulation and invalid expansions.
Enforced by:
- `docs/arch/INVARIANTS_AND_TOLERANCES.md`
- Tests: `tests/app/scale0_contract_tests.py`

## Invariant: Interest drives activation (SCALE0-INTEREST-006)
Why:
- Activation must be explicit, deterministic, and auditable.
Breaks if violated:
- View-driven activation, hidden work, and nondeterministic scaling.
Enforced by:
- `docs/arch/INTEREST_MODEL.md`
- Tests: `tests/app/scale0_contract_tests.py`

## Invariant: No ex nihilo expansion (SCALE0-NO-EXNIHILO-007)
Why:
- Expansion must reconstruct, not invent.
Breaks if violated:
- Fabricated entities/resources and broken conservation.
Enforced by:
- `docs/arch/COLLAPSE_EXPAND_CONTRACT.md`
- Tests: `tests/app/scale0_contract_tests.py`

## Invariant: Replay equivalence across collapse/expand (SCALE0-REPLAY-008)
Why:
- Save/replay integrity depends on identical macro transitions.
Breaks if violated:
- Replays diverge when collapse/expand occurs.
Enforced by:
- `docs/arch/MACRO_TIME_MODEL.md`
- `docs/arch/REPLAY_FORMAT.md`
- Tests: `tests/app/scale0_contract_tests.py`

## Invariant: Scaling work is budget-gated (SCALE3-BUDGET-009)
Why:
- Budgets are the only lawful way to bound work without changing semantics.
Breaks if violated:
- Hidden scaling paths bypass policy and destroy auditability.
Enforced by:
- `docs/arch/BUDGET_POLICY.md`
- `docs/arch/CONSTANT_COST_GUARANTEE.md`
- Tests: `tests/app/scale3_budget_tests.py`

## Invariant: Admission control is explicit and non-mutating on refusal (SCALE3-ADMISSION-010)
Why:
- Refusal and defer semantics are part of determinism and replay guarantees.
Breaks if violated:
- Budget pressure silently changes outcomes or corrupts state.
Enforced by:
- `docs/arch/BUDGET_POLICY.md`
- `docs/arch/REFUSAL_SEMANTICS.md`
- Tests: `tests/app/scale3_budget_tests.py`

## Invariant: Per-commit cost is bounded by active fidelity (SCALE3-CONSTCOST-011)
Why:
- Large worlds and deep history must not change active simulation cost.
Breaks if violated:
- Cost scales with world size, time span, or collapsed-domain count.
Enforced by:
- `docs/arch/CONSTANT_COST_GUARANTEE.md`
- `docs/arch/MACRO_TIME_MODEL.md`
- Tests: `tests/app/scale3_budget_tests.py`

## Forbidden assumptions
- Invariants are optional or "guidelines" rather than binding rules.
- Convenience exceptions are acceptable without a canon update.

## Dependencies
- `docs/arch/ARCH0_CONSTITUTION.md`
- `docs/arch/CHANGE_PROTOCOL.md`

## See also
- `docs/arch/CANONICAL_SYSTEM_MAP.md`
- `docs/arch/REALITY_MODEL.md`
- `docs/arch/AUTHORITY_MODEL.md`
- `docs/arch/EXECUTION_MODEL.md`
