Status: CANONICAL
Last Reviewed: 2026-04-04
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: next checkpoint before Φ-B4, risky Φ-B4, risky Φ-B5, later publication and trust operational doctrine, future Ζ planning
Replacement Target: later release-ops, publication, trust, archive, and live-ops operational doctrine may refine procedures and tooling without replacing the execution-envelope semantics frozen here
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/CHECKPOINT_C_YA_SAFE_REVIEW.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_YA.md`, `docs/agents/AGENT_TASKS.md`, `docs/agents/XSTACK_TASK_CATALOG.md`, `docs/agents/MCP_INTERFACE_MODEL.md`, `docs/agents/AGENT_SAFETY_POLICY.md`, `docs/runtime/EVENT_LOG_AND_REPLAY_DOCTRINE.md`, `docs/runtime/SNAPSHOT_SERVICE_DOCTRINE.md`, `docs/runtime/SANDBOXING_AND_ISOLATION_MODEL.md`, `docs/runtime/LIFECYCLE_MANAGER.md`, `docs/runtime/MULTI_VERSION_COEXISTENCE.md`, `docs/release/BUILD_GRAPH_LOCK.md`, `docs/release/VERSIONING_CONSTITUTION.md`, `docs/release/RELEASE_CONTRACT_PROFILE.md`, `docs/release/RELEASE_INDEX_AND_RESOLUTION_ALIGNMENT.md`, `docs/release/OPERATOR_TRANSACTION_AND_DOWNGRADE_DOCTRINE.md`, `docs/release/OPERATOR_TRANSACTION_RECEIPTS_AND_PROVENANCE_CONTINUITY.md`, `docs/release/ARCHIVE_AND_MIRROR_CONSTITUTION.md`, `docs/release/PUBLICATION_TRUST_AND_LICENSING_GATES.md`, `docs/release/MANUAL_AUTOMATION_PARITY_AND_REHEARSAL.md`, `tools/controlx/README.md`, `tools/controlx/controlx.py`, `tools/controlx/core/execution_router.py`, `tools/controlx/core/queue_runner.py`, `tools/xstack/sessionx/stage_parity.py`, `tools/xstack/testx/tests/test_dryrun_tool_runs.py`, `release/update_resolver.py`, `repo/release_policy.toml`, `updates/README.md`, `data/registries/release_resolution_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `data/registries/refusal_code_registry.json`, `data/registries/remediation_playbooks.json`

# Release Ops Execution Envelope

## A. Purpose And Scope

This doctrine exists to freeze the canonical meaning of the release-ops execution envelope inside the narrow post-`Υ-A`, post-`Φ-B3`, and post-`Υ-B1` operational-alignment band chosen by `C-ΥA_SAFE_REVIEW`.

It solves a specific problem: the repository already contains real release and control-plane execution surfaces across ControlX, XStack, release resolution, transaction logging, archive history retention, trust policies, and publication gates. Without one explicit doctrine, later work could still drift into unsafe folklore:

- every release/control-plane action being treated as equally executable
- dry-run, rehearsal, review, approval, and privileged execution being blurred together
- task-catalog or MCP exposure being mistaken for execution authority
- operator tooling becoming the real policy engine
- release-ops maturity being inferred from scripts or wrappers rather than from doctrine

This document governs:

- what a release-ops execution envelope is in Dominium
- which release and control-plane actions fall inside the envelope
- how those actions are classified across inspect, plan, rehearse, validate, bounded mutate, review-gated execute, privileged execute, and prohibit posture
- which dimensions determine that posture
- how execution posture remains subordinate to governance, safety, release, receipt, and runtime doctrine
- what later checkpoints, risky `Φ-B4`, risky `Φ-B5`, publication and trust execution work, and future `Ζ` planning must consume rather than reinvent

It does not govern:

- deployment-engine implementation
- live cutover workflow implementation
- publication automation
- trust-root or licensing execution systems
- distributed authority implementation
- hotswap implementation

This is a constitutional execution-boundary standard, not execution tooling.

## B. Core Definition

A release-ops execution envelope in Dominium is the canonical classification layer that says how a release or control-plane action may lawfully be handled at the current maturity level.

The envelope answers questions such as:

- may this action only be inspected
- may it be planned but not run
- may it be rehearsed or dry-run
- may it be structurally validated
- may it perform bounded mutation
- does it require explicit review-gated execution
- is it privileged and operator-only
- is it non-executable or prohibited in the current maturity state

This differs from nearby surfaces:

- task catalog
  - describes work families and invocation shapes, not the final execution posture
- MCP exposure
  - exposes interfaces, not execution authority
- safety policy
  - remains upstream on permission posture; the envelope specializes release/control-plane execution classes under that law
- operator transactions
  - define typed control-plane meaning; the envelope defines what execution posture that meaning may inhabit
- release pipeline implementation
  - implements procedures; the envelope constrains what kinds of procedures may exist or remain gated
- live-ops implementation
  - remains later and more dangerous than this doctrine

The envelope is therefore a layered posture model, not a yes-or-no flag.

## C. Why An Execution Envelope Is Necessary

An execution envelope is necessary because release and control-plane work is not a flat category.

The repo already shows distinct posture layers:

- `tools/controlx/core/execution_router.py` explicitly distinguishes dry-run from live routing and remediation-aware gate orchestration
- `tools/controlx/core/queue_runner.py` records canonical run logs and escalation outcomes, proving that execution posture is already more than "just run it"
- `release/update_resolver.py` performs governed selection and rollback-oriented transaction logging, proving that release-control actions already carry typed consequences
- `repo/release_policy.toml` constrains branch, kind, and channel combinations, proving that even basic release movement is policy-shaped
- `data/registries/trust_policy_registry.json` is still provisional and `data/registries/trust_root_registry.json` is empty, proving that some trust-bearing actions are still constitutionally immature

Without an explicit envelope, later work would drift toward:

- rehearsal being confused with live permission
- publication-adjacent actions being confused with bounded metadata edits
- tool wrappers silently defining what is executable
- runtime-sensitive release actions being handled like ordinary control metadata

The envelope therefore exists to keep execution maturity explicit and non-silent.

## D. Action Classes Inside The Envelope

The constitutional execution classes are:

### D1. Inspect-Only

Actions that read or surface current release, archive, trust, policy, or receipt state without mutating authoritative control-plane truth.

Examples:

- release-index inspection
- transaction receipt inspection
- archive-history inspection
- trust-policy inspection

### D2. Planning-Only

Actions that describe intended work, candidate selection paths, review posture, or next-step recommendations without mutating authoritative release state.

Examples:

- checkpointing
- release-ops sequencing
- operator remediation planning
- publication readiness planning

### D3. Rehearse-Able

Actions that may be exercised through dry-run, preflight, simulation, or typed rehearsal without claiming live completion.

Examples:

- release-selection rehearsal
- rollback or downgrade rehearsal
- archive-readiness rehearsal
- gate routing rehearsal through ControlX dry-run surfaces

### D4. Validate-Able

Actions that may be structurally validated for admissibility, completeness, compatibility, or policy readiness without necessarily becoming live execution.

Examples:

- manifest validation
- release-contract-profile compatibility checks
- trust-policy admissibility checks
- archive completeness checks

### D5. Bounded Mutation

Actions that may lawfully mutate bounded control-plane or support state without crossing public-commitment, trust-root, or live-runtime cutover boundaries.

Examples:

- deterministic support-artifact regeneration
- bounded control-plane metadata repair
- receipt-bearing non-public state annotation where later doctrine permits it

### D6. Review-Gated Execution

Actions that may execute only under explicit human review because their blast radius, continuity effect, or release-facing meaning exceeds routine bounded mutation.

Examples:

- governed rollback or downgrade execution
- yank, supersession, or recovery execution
- high-impact visibility or eligibility changes

### D7. Privileged Execution

Actions whose public-commitment, trust-bearing, licensing-bearing, or high-irreversibility posture keeps them under privileged or operator-only execution rules.

Examples:

- publication approval execution
- trust-posture or signing-posture mutation
- licensing-posture mutation

### D8. Non-Executable Or Prohibited

Actions that current doctrine or current maturity does not permit to be executed, even if the repo can describe them.

Examples:

- live cutover claims that exceed current runtime maturity
- trust-root mutation by convenience
- hotswap-by-stealth
- distributed authority handoff or live shard relocation claims

An action may move through multiple classes over time. For example, a release action can be inspectable, then rehearse-able, then review-gated for live execution. The envelope classifies posture, not permanent identity.

## E. Envelope Dimensions

Execution posture is evaluated across the following dimensions:

- blast radius
  - how much release, operator, archive, trust, or user-visible state can be affected
- reversibility
  - whether the action is reversible, partially reversible, or effectively irreversible
- provenance and receipt requirement
  - what canonical evidence must exist before and after the action
- release-identity impact
  - whether the action changes identity, visibility, selection, or only inspection posture
- compatibility-envelope impact
  - whether the action depends on or changes admissibility relative to release contract profile and resolution law
- archive and mirror impact
  - whether the action changes retention, visibility, availability, or continuity interpretation
- publication and trust impact
  - whether the action changes external commitment, authenticity posture, or rights posture
- runtime-sensitivity impact
  - whether lifecycle, replay, snapshot, isolation, or coexistence assumptions are implicated
- parity and rehearsal availability
  - whether lawful manual and automated parity exists and whether meaningful rehearsal exists
- human review requirement
  - whether execution requires review, privileged approval, or must remain blocked

No single dimension decides posture by itself. The envelope exists precisely because release/control-plane actions are multi-dimensional.

## F. Relationship To Task Catalog And MCP

Cataloged does not mean executable.
Exposed does not mean executable.
Exposed does not mean permitted.

The governing consequences are:

- task catalog defines work vocabulary, not execution authority
- MCP exposure defines surface availability, not live execution approval
- a surface may support inspect-only or rehearse-able posture while live execution remains review-gated or prohibited
- the envelope specializes execution posture over already-defined task and interface surfaces

Tool presence, command availability, or endpoint reachability must not silently become execution law.

## G. Relationship To Safety Policy

Safety policy remains upstream.

This doctrine does not create permission. It refines release/control-plane execution posture specifically.

The governing consequences are:

- inspect-only and planning-only actions may still be lawful where live mutation is not
- rehearsal and validation may be lawful where privileged execution is not
- review-gated and privileged execution remain constrained by safety classes
- prohibited actions remain prohibited even if a tool can technically express them

The envelope therefore consumes safety posture; it never overrides it.

## H. Relationship To Operator Transaction And Receipts

Execution classes must remain compatible with typed operator transactions and with canonical receipts and provenance continuity.

The governing consequences are:

- a review-gated rollback is still a rollback, not generic mutation
- a privileged publication action is still publication-bearing, not ordinary control metadata
- receipt expectations must remain visible per posture
- blocked, refused, rehearsed, and completed outcomes must remain distinguishable in receipt form where receipt-bearing classes apply

Execution envelope posture must therefore preserve transaction semantics rather than flatten them.

## I. Relationship To Release Doctrine

Release doctrine remains upstream.

The governing consequences are:

- build graph lock remains upstream on structure
- versioning constitution remains upstream on version meaning
- release contract profile remains upstream on compatibility truth
- release index and resolution remain upstream on selection truth
- archive and mirror constitution remains upstream on retention and availability meaning
- publication, trust, and licensing gates remain upstream on external commitment posture

Execution posture cannot replace compatibility truth or release identity truth. It only classifies how governed action may proceed under those truths.

## J. Relationship To Runtime Doctrine

Release/control-plane execution must not overclaim runtime maturity.

If an action interacts with runtime-sensitive areas, it must respect:

- lifecycle boundaries
- replay boundaries
- snapshot boundaries
- isolation boundaries
- coexistence boundaries

The governing consequences are:

- rehearsal does not prove live cutover safety
- release-control execution does not by itself prove hotswap legality
- coexistence does not by itself prove runtime replacement safety
- release tooling must not flatten runtime-sensitive actions into metadata edits

This remains especially important for the next checkpoint before any move into `Φ-B4`.

## K. Invalidity And Blocked Actions

Actions may be:

- blocked
- under-specified
- policy-gated
- safety-gated
- receipt-incomplete
- continuity-incomplete
- non-rehearsable
- non-reversible
- trust-posture immature
- runtime-sensitive beyond current foundation
- prohibited

Later tools must not assume all actions fit one posture or that every failure is the same kind of failure.

In particular:

- a rehearsable action is not necessarily live-executable
- a validatable action is not necessarily mutation-capable
- a review-gated action is not the same as a privileged action
- a privileged action is not automatically available merely because an operator tool exists

## L. Canonical Vs Derived Distinctions

Canonical execution-envelope surfaces include:

- this doctrine
- its paired machine-readable registry
- upstream safety, operator, receipt, release, runtime, and checkpoint doctrine
- governed execution decisions where later doctrine explicitly defines them

Derived surfaces include:

- UI flows
- CLI wrappers
- dashboards
- queue summaries
- dry-run output text
- generated feed summaries
- helper scripts and convenience reports

Derived representations may expose or summarize execution posture, but they must not redefine it.

## M. Ownership And Anti-Reinvention Cautions

The repo-wide cautions remain fully active:

- `fields/` remains canonical semantic field substrate; `field/` remains transitional
- `schema/` remains canonical semantic contract law; `schemas/` remains projection-facing
- `packs/` remains canonical for runtime packaging and activation scope; `data/packs/` remains scoped authored-pack authority in residual split territory
- canonical versus projected/generated distinctions remain binding
- planning drift and stale numbering do not override the active checkpoint chain
- execution-envelope doctrine must be extracted from current repo reality rather than invented greenfield

Additional caution:

- thin operational roots such as `tools/controlx/`, `tools/xstack/`, `release/`, `updates/`, or `security/trust/` are important evidence surfaces, but none of them alone becomes execution canon by convenience

## N. Anti-Patterns And Forbidden Shapes

The following shapes are constitutionally forbidden:

- cataloged therefore executable
- exposed therefore executable
- rehearsal therefore live-approved
- validation pass therefore privileged execution allowed
- privileged action treated like bounded mutation
- release-control action treated like ordinary metadata edit
- tool wrapper defines execution posture by convenience
- dry-run output treated as live completion
- runtime-sensitive release action treated as if replay, snapshot, isolation, and coexistence no longer matter
- empty or provisional trust surfaces treated as if trust execution maturity already exists

## O. Stability And Evolution

This artifact is `provisional` but canonical.

It directly enables:

- the next checkpoint before any move into `Φ-B4`
- later guarded reassessment of `Φ-B4` and `Φ-B5`
- future release-ops, publication, trust, and live-ops planning with clearer execution-boundary maturity
- future `Ζ` blocker reduction around operational-boundary maturity

Updates must remain:

- explicit
- auditable
- non-silent about changed execution posture
- non-silent about changed receipt requirements
- non-silent about changed runtime-sensitivity claims

Later work may refine operational procedures and tools, but it may not silently:

- collapse the envelope into a boolean allowed/disallowed flag
- let tool exposure become execution authority
- let rehearsal become live approval
- let release-control convenience outrun runtime or trust maturity
