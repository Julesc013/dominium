Status: CANONICAL
Last Reviewed: 2026-04-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Φ-B, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/agents/AGENT_TASKS.md`, `docs/agents/AGENT_MIRROR_POLICY.md`, `docs/agents/NATURAL_LANGUAGE_TASK_BRIDGE.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/POST_PI_EXECUTION_PLAN.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_POST_SIGMA_B_PRE_PHIB_UPSILON.md`, `docs/planning/NEXT_TWO_SERIES_PLAN_PHIB_UPSILON.md`, `docs/runtime/RUNTIME_KERNEL_MODEL.md`, `docs/runtime/COMPONENT_MODEL.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/runtime/DOMAIN_SERVICE_BINDING_MODEL.md`, `docs/runtime/STATE_EXTERNALIZATION.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_CAPABILITY_SURFACES.md`, `specs/reality/SPEC_REPRESENTATION_LADDERS.md`, `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`

# Dominium Sandboxing And Isolation Model

## 1. Purpose And Scope

`SANDBOXING_AND_ISOLATION_MODEL.md` defines the canonical constitutional law for sandboxing and isolation in Dominium.

It exists because post-`Λ`, post-`Σ-B`, and post-`Φ-B1` Dominium now has explicit law for:

- semantic truth, ownership, bridges, representation, and formalization
- governance, task, MCP, and safety boundaries
- kernel, component, service, binding, state, lifecycle, replay, and snapshot boundaries

Isolation doctrine is the missing containment layer that explains how runtime subjects, mutation surfaces, visibility surfaces, and tool-mediated actions may be separated, narrowed, exposed, or quarantined without letting operational convenience redefine truth, authority, or lawful continuity.

This artifact governs:

- what sandboxing and isolation mean in Dominium
- what kinds of subjects and surfaces require isolation boundaries
- what classes of isolation boundaries exist
- how isolation must remain subordinate to semantic, governance, runtime, replay, and snapshot law
- what invalidity, degradation, and review cautions later work must preserve

This artifact does not implement:

- OS process isolation
- containers, VMs, or namespaces
- capability sandbox machinery
- remote execution systems
- multi-version coexistence
- hotswap
- distributed authority transfer
- live-ops control stacks

Those later prompts must consume this doctrine rather than inventing their own containment semantics.

This is a post-`Σ-B` / post-`Φ-A2` / post-`Φ-B1` artifact. It carries forward the checkpoint judgment that sandboxing and isolation are `ready_with_cautions`, while multi-version coexistence remains blocked and hotswap plus distributed authority remain dangerous and review-gated.

Repo-grounded extension surfaces already exist and must be treated as evidence rather than as automatic canon:

- `app/readonly_adapter.c`
- `app/readonly_format.c`
- `process/capsules/capsule_executor.py`
- `control/control_plane_engine.py`
- `client/local_server/local_server_controller.py`
- `net/policies/policy_server_authoritative.py`
- `tools/xstack/testx/tests/test_renderer_truth_isolation.py`
- `tools/xstack/testx/tests/test_platform_isolation.py`
- `tools/xstack/testx/tests/test_no_production_import_from_quarantine.py`
- `docs/control/CONTROL_PLANE_CONSTITUTION.md`

## 2. Core Definition

In Dominium, isolation is the declared, auditable, law-governed separation of authority posture, state posture, execution posture, visibility posture, tool posture, or continuity posture between runtime subjects or surfaces.

In Dominium, sandboxing is a constrained operational posture inside an isolation boundary that deliberately narrows what a subject, interface, or execution context may observe, mutate, invoke, emit, import, or claim.

They are related but not identical:

- isolation is the broader boundary grammar
- sandboxing is one kind of constrained posture inside that grammar
- all sandboxes are isolation boundaries
- not all isolation boundaries are sandboxes

Sandboxing and isolation are distinct from nearby concepts:

- Mere debugging or test environments
  - a test environment may exist without lawful authority, state, or bridge separation
- Access control alone
  - permission checks are only one part of an isolation boundary
- Lifecycle alone
  - lifecycle changes posture over time but does not by itself define separation boundaries
- State externalization alone
  - state law constrains isolation but does not define containment classes by itself
- Remote execution alone
  - remoteness is implementation topology, not constitutional isolation law
- Release or control-plane gating
  - release and control planes consume isolation law later; they do not define it here
- Future live-ops implementations
  - live-ops is a later operational consumer, not the source of boundary meaning

Isolation therefore is not a synonym for "test mode," "dev mode," "remote mode," or "readonly mode." It is a broader constitutional containment model.

## 3. Why Isolation Law Is Necessary

Bounded execution and bounded exposure require lawful separation.

Without explicit isolation law, later architecture tends to collapse into unsafe shortcuts:

- "sandbox" used to mean only a playtest or developer environment
- runtime convenience bypassing ownership or bridge law once work crosses a boundary
- projected or generated artifacts escaping their lawful containment and being treated as canonical
- replay or snapshot support becoming unreconstructable because a boundary was not declared
- control-plane, product, or tool surfaces silently acting as authority surfaces
- multi-version, hotswap, downgrade, or distributed-authority work inheriting undefined containment assumptions

Isolation doctrine is therefore necessary for:

- safety and bounded exposure
- preservation of ownership and bridge legality
- replay integrity
- snapshot legality
- state-class preservation
- future operational flexibility without hidden semantic drift

Convenience must not substitute for lawful isolation boundaries.

## 4. Isolation Subjects

Isolation law applies to runtime subjects and boundary-relevant surfaces, not to semantic domains themselves.

### 4.1 Kernel-Adjacent Runtime Structures

Execution-hosting and execution-coordinating structures may require isolation because deterministic execution, legal visibility, or bounded hosting does not imply unrestricted access or mutation.

### 4.2 Runtime Services

Services may require isolation when mediation, routing, authority handling, replay support, snapshot handling, compatibility handling, or control exposure would otherwise blur runtime and semantic authority.

### 4.3 Component Groups

Groups of bounded components may require isolation when shared execution or state locality would otherwise cause hidden coupling, hidden truth ownership, or hidden bridge bypass.

### 4.4 Domain-Support Structures

Runtime structures that support observation, validation, persistence support, replay support, or other domain-adjacent behavior may require isolation so that support does not become semantic ownership.

### 4.5 Control And Integration Structures

Control-plane, negotiation, routing, policy, transport, and integration surfaces may require isolation because they are close to authority envelopes without being semantic owners.

### 4.6 Observation And Presentation Support Structures

Read-only adapters, render pipelines, inspection tools, and presentation surfaces may require isolation so that visibility remains downstream of truth.

### 4.7 Tool-Mediated Mutation Surfaces

CLI, MCP, automation, and operator-mediated mutation paths may require stronger isolation because tool reachability is not permission, and boundary bypass through tooling is constitutionally forbidden.

### 4.8 Experimental Or Provisional Runtime Structures

Provisional, playtest, research, or diagnostic structures may require explicit isolation so that they remain bounded evidence or bounded experimentation rather than silent canonical authority.

### 4.9 Later Module Realizations

Later module or packaging realizations may embody isolated subjects, but physical module layout is implementation evidence rather than constitutional boundary law.

## 5. Isolation Boundary Classes

The boundary taxonomy is constitutional and intentionally general.

### 5.1 Authority And Ownership Isolation

This boundary class preserves semantic ownership and authority posture so that shared hosting, convenience roots, or tool reachability do not become ownership reassignment.

### 5.2 State Isolation

This boundary class preserves authoritative, derived, transient, projected, and presentation state distinctions so that boundary crossing does not silently promote or trap state classes.

### 5.3 Execution Isolation

This boundary class constrains what execution contexts may run, mutate, schedule, or import so that runtime adjacency does not create uncontrolled side effects.

### 5.4 Bridge-Mediated Isolation

This boundary class preserves explicit separation for cross-domain or cross-shard effects whose legality depends on bridge law rather than on local convenience.

### 5.5 Replay And Snapshot Isolation

This boundary class preserves lawful read-only reenactment, lawful continuity capture, and lawful replay/snapshot interpretation without allowing replay or snapshot surfaces to mutate truth or erase lineage.

### 5.6 Observation And Presentation Isolation

This boundary class preserves the distinction between visibility and authority so that render, UI, observability, and inspection surfaces remain downstream of truth.

### 5.7 Control-Plane And Tool Isolation

This boundary class constrains control, CLI, automation, MCP, and operator surfaces so that exposure, orchestration, or policy mediation does not become hidden execution authority.

### 5.8 Provisional And Experimental Isolation

This boundary class keeps experimental, diagnostic, or playtest work explicitly quarantined so that provisional behavior does not silently become default runtime authority.

## 6. Isolation Relationship To Truth

Isolation boundaries must not redefine semantic truth.

The governing rules are:

- isolated subjects may still operate over the same lawful truth substrate under explicit rules
- lack of visibility or access within one boundary does not imply nonexistence of truth outside it
- bounded exposure is not ontology
- isolated execution posture does not authorize truth reinterpretation
- total truth and sparse materialization remain binding across isolation boundaries

Isolation therefore may narrow visibility, mutability, or transport without changing what truth is.

## 7. Isolation Relationship To Ownership

Isolation must respect semantic ownership review.

The governing rules are:

- canonical versus projected or generated distinctions remain binding inside isolated contexts
- isolation boundaries must not silently reassign authority across roots
- convenience roots do not become canonical because they are easier to isolate
- shared execution, shared transport, or shared tooling does not create shared ownership
- ownership-sensitive root cautions remain active inside all boundary classes

An isolated context cannot make a projection canonical by enclosing it.

## 8. Isolation Relationship To Bridges

Cross-domain effects remain bridge-mediated.

The governing rules are:

- isolation must not hide or bypass bridge legality
- bridge-mediated operations may require stronger boundary classes because local safety assumptions do not transfer automatically across domains
- a boundary that encloses more than one domain must still preserve domain identity and declared mediation posture
- boundary crossing cannot convert mediated legality into local direct authority

Some isolation boundaries exist precisely because bridge interaction is constrained, high-risk, or review-heavy.

## 9. Isolation Relationship To State Externalization

Isolation must remain compatible with state externalization law.

The governing rules are:

- isolated execution may host transient state, but it may not trap authoritative truth illicitly
- authoritative, derived, transient, projected, and presentation state classes remain binding across isolation boundaries
- state transitions across boundaries must remain explicit enough for lawful audit, replay, and snapshot interpretation
- isolated projected or generated state remains non-canonical unless stronger law promotes it
- hidden service-local or tool-local state is not legitimized merely because it sits inside a sandbox

Isolation therefore narrows operational posture without creating new exceptions to state law.

## 10. Isolation Relationship To Lifecycle

Lifecycle and isolation must remain compatible.

Lifecycle transitions may create, enter, leave, suspend, degrade, block, fail, or retire isolated boundaries.

The governing rules are:

- lifecycle convenience must not dissolve isolation boundaries implicitly
- degraded, blocked, or failed posture may alter visibility, throughput, or allowed actions without altering underlying ownership or truth
- suspension or quiescence does not erase the boundary history or boundary obligations
- boundary creation and boundary removal must remain auditable in principle

Isolation is therefore a boundary posture grammar, not a substitute lifecycle state machine.

## 11. Isolation Relationship To Replay And Snapshots

Replay doctrine and snapshot doctrine remain upstream constraints on isolation.

The governing rules are:

- isolation boundaries must not make authoritative history unreconstructable without declared lawful reason
- isolation boundaries must not make lawful snapshots uninterpretable or falsely authoritative
- replay-only contexts may be read-only or otherwise narrowed, but reenactment posture does not create mutation authority
- snapshot-support boundaries may capture lawful continuity anchors, but they do not replace replay lineage
- replay and snapshot compatibility may later narrow which isolation classes are lawful for privileged continuity work

Isolation must therefore preserve continuity support rather than obstruct it by convenience.

## 12. Isolation Relationship To Capability Surfaces

Capability surfaces may be exposed differently across isolation boundaries, but capability meaning remains upstream.

The governing rules are:

- isolation may constrain visibility, usability, authority envelope, or degraded access
- isolation may support explicit refusal, downgrade, or read-only posture
- isolation may not redefine what a capability means semantically
- isolation may not create hidden super-capabilities inside a sandbox merely because the boundary is narrow

Isolation changes posture, not capability semantics.

## 13. Isolation Relationship To Products, Mirrors, And MCP

Product, mirror, and tool boundaries are not sufficient isolation law by themselves.

The governing rules are:

- product or session boundaries are not universal runtime isolation boundaries
- mirror files do not define isolation law
- MCP exposure must remain subordinate to isolation rules
- exposed tasks do not imply boundary bypass
- tool mediation, CLI reachability, or remote access do not create mutation authority
- a product shell may consume isolated surfaces, but product UX language does not define containment legality

Product/session boundaries are therefore insufficient because they describe user experience shells, not the underlying authority, state, bridge, replay, snapshot, or control separation required by runtime law.

## 14. Isolation Invalidity And Failure

Not all isolation mechanisms or postures are equally lawful.

Possible validity or degradation postures include:

- complete
- partial
- degraded
- misconfigured
- under-authorized
- ownership-invalid
- bridge-invalid
- state-trapping
- replay-snapshot-incompatible
- projection-leaking
- visibility-authority-confused
- unsafe-for-privileged-or-cross-boundary use

Later systems must not assume that all boundaries marketed as "sandboxed" are equally strong, equally lawful, or equally fit for privileged or continuity-sensitive work.

## 15. Verification And Auditability

Isolation doctrine must support auditability and testability in principle.

Later systems should be able to verify:

- ownership legality across boundaries
- bridge legality across boundaries
- preservation of state classes across boundaries
- replay and snapshot compatibility
- visibility versus authority distinctions
- degraded versus lawfully isolated posture
- whether projected or provisional material remained properly contained

This doctrine therefore requires isolation semantics to stay explicit enough for review rather than disappearing into implementation-specific marketing terms.

## 16. Ownership And Anti-Reinvention Cautions

The following cautions remain binding for isolation doctrine:

- `fields/` is canonical semantic field substrate; `field/` remains a transitional compatibility facade
- `schema/` is canonical semantic contract law; `schemas/` remains a validator-facing projection or advisory mirror
- `packs/` is canonical in runtime packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/` remains authoritative within authored pack content and declaration scope, but stays transitional and residual-quarantined for attempted single-root convergence
- canonical versus projected/generated distinctions remain binding
- the thin `runtime/` root is not automatically canonical just because it is runtime-adjacent
- older planning numbering drift does not override the active checkpoint path

Isolation law must be extracted from current doctrine and repo reality, not invented greenfield. Existing read-only, replay-only, authority-gated, renderer-isolated, quarantine, and policy-mediated surfaces are evidence to extend carefully, not permission to infer stronger guarantees than the repo or doctrine actually establishes.

## 17. Anti-Patterns And Forbidden Shapes

The following shapes are forbidden:

- using `sandbox` as a vague synonym for test mode or developer convenience
- hidden authority reassignment through isolation boundaries
- isolated projected or generated state treated as canonical truth
- boundaries that ignore replay or snapshot law
- MCP, CLI, or tool exposure bypassing isolation
- product or session shells treated as sufficient isolation law
- bridge-mediated operations treated as local safe operations by default
- isolation defined solely by one implementation technology
- isolation that traps authoritative truth or erases state-class distinctions
- isolation that hides degraded or unsafe posture behind reassuring labels

## 18. Stability And Evolution

This artifact is `canonical` but `provisional`.

It is stable enough to guide downstream work, but it is expected to be refined explicitly by later prompts that consume it, especially:

- later checkpoint reconsideration of `Φ-B3` multi-version coexistence
- later checkpoint reconsideration of `Φ-B4` hotswap boundaries
- later checkpoint reconsideration of `Φ-B5` distributed authority foundations
- `Υ` work involving control-plane posture, operator transaction caution, archive and downgrade boundaries, and release-adjacent containment
- later `Ζ` work involving multi-version, restartless, recovery, and live-ops gating

This model does not automatically unblock blocked or dangerous `Φ-B` tail work. It gives later checkpoints and later prompts a constitutional isolation floor to evaluate against.

Any update to this doctrine must remain:

- explicit
- auditable
- non-silent
- subordinate to semantic law, ownership review, bridge law, state law, lifecycle law, replay law, snapshot law, and the completed governance/safety stack

Isolation in Dominium is therefore a constitutional containment model, not a shortcut around authority, continuity, or review.
