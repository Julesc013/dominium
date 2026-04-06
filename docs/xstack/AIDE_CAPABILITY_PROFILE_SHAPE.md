Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: X-6, AIDE extraction review
Replacement Target: later explicit portable capability-profile checkpoint or replacement artifact only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`, `docs/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`, `data/xstack/xstack_inventory_and_classification.json`, `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`, `data/xstack/aide_portable_task_contract.json`, `docs/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`, `data/xstack/aide_evidence_and_review_contract.json`, `docs/xstack/AIDE_POLICY_AND_PERMISSION_SHAPE.md`, `data/xstack/aide_policy_and_permission_shape.json`, `data/registries/capability_registry.json`, `data/registries/platform_capability_registry.json`, `data/registries/product_capability_defaults.json`, `data/registries/tool_capability_registry.json`, `data/registries/server_profile_registry.json`, `data/registries/law_profiles.json`, `data/registries/degrade_ladder_registry.json`, `data/registries/compat_mode_registry.json`, `data/registries/semantic_contract_registry.json`, `compat/descriptor/descriptor_engine.py`, `compat/capability_negotiation.py`, `appshell/ui_mode_selector.py`, `appshell/command_registry.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `server/server_boot.py`, `server/net/loopback_transport.py`, `client/interaction/affordance_generator.py`, `validation/validation_engine.py`, `tools/xstack/testx/tests/test_required_cap_mismatch_refuses.py`, `tools/xstack/testx/tests/test_unknown_cap_ignored.py`, `tools/xstack/testx/tests/test_cross_platform_caps_degrade_consistent.py`

# AIDE Capability Profile Shape

## A. Purpose and Scope

This artifact freezes the canonical portable capability-profile shape that later XStack/AIDE prompts may reuse.

It exists because:

- `X-0` froze what XStack means now and what stays outside the current series
- `X-1` classified which live surfaces are portable core, runtime, ops, Dominium-retained, legacy, or mixed
- `X-2` froze the portable task unit and required explicit suitability, permission, and refusal boundaries
- `X-3` froze portable evidence and review, which capability compatibility and exceptions may need to reference
- `X-4` froze portable policy and permission posture, which capability declarations may link to without becoming enforcement
- later extraction work still needs a smaller and stricter contract for capability-profile truth itself

This artifact solves a specific narrowing problem:

- the live repo already has product capability defaults, platform capability matrices, tool capability rows, law and server profiles, semantic contract ranges, degrade ladders, compatibility modes, and runtime selectors
- later AIDE work needs the portable minimum those surfaces imply
- that portable minimum must be frozen without smuggling in platform probing, activation, scheduling, adapter runtime, or product-shell dispatch

This artifact governs:

- what a portable capability profile means in the live XStack/AIDE sense
- which fields every canonical portable capability profile must expose
- which boundaries must remain explicit
- how capability profiles relate to the prior portable task, evidence/review, and policy/permission contracts
- which parts are portable now versus Dominium-retained now versus deferred until after the playable baseline exists
- which later prompts may treat this artifact as their fact base

This artifact is downstream of `X-0` through `X-4`.
It does not reopen scope, inventory, task, evidence/review, or policy/permission classification.
It narrows those earlier artifacts into portable capability-profile truth only.

This artifact must preserve current repo reality:

- admissible `Zeta` doctrine and gating work is complete
- the immediate product priority remains the canonical repo-local playable baseline and repo stabilization
- XStack/AIDE work must support clarification, modularization, and contract extraction without competing with the baseline path

This artifact is a contract freeze.
It does not implement a runtime capability resolver, daemon, scheduler, registry service, adapter runtime, compiler, or broader AIDE platform.

## B. Current-State Definition of a Portable Capability Profile

Current definition:

A portable capability profile is a canonical declarative profile that states which capability classes a subject, endpoint, product, platform, or governed bundle declares as supported, conditionally supported, excluded, or dependency-bound; what constraints and compatibility ranges qualify those declarations; what policy or permission surfaces they depend on; what tasks they are suitable for or exclude; and what evidence, review, version, stability, and portability limits apply, without embedding runtime capability probing, profile activation, negotiation, or host-specific fallback execution.

The portable capability-profile shape is:

- a contract for declared capability posture
- a contract for required versus optional dependencies
- a contract for exclusions, limits, and compatibility notes
- a contract for how task, evidence/review, and policy/permission contracts may link to declared capabilities

The portable capability-profile shape is not:

- a runtime capability resolver
- a platform probe
- an activation plan
- an attach or launch decision
- a negotiated compatibility record
- an AppShell mode-selection result
- a queue, scheduler, or adapter transport declaration

The portable model must distinguish the following.

### Canonical Capability Profile

Canonical capability profile truth lives in contract-bearing profile rows, defaults, matrices, or equivalent declarative artifacts.

The live repo shows this shape through:

- `data/registries/product_capability_defaults.json`
- `data/registries/platform_capability_registry.json`
- `data/registries/tool_capability_registry.json`
- `data/registries/server_profile_registry.json`
- `data/registries/law_profiles.json`

These surfaces differ in ownership and portability, but they share a common declarative pattern:

- stable profile or subject identity
- declared capability or entitlement posture
- required and optional dependencies
- linked policy ids
- explicit exclusions, gates, or conditions
- stability or compatibility markers

That shared declarative pattern is what this artifact freezes.

### Derived Profile Views and Summaries

Derived profile views are rendered summaries, selector tables, CLI help, status output, compatibility reports, or UI cards that surface capability posture without redefining it.

Examples in the live repo include:

- endpoint descriptors emitted by `compat/descriptor/descriptor_engine.py`
- AppShell mode-selection status from `appshell/ui_mode_selector.py`
- command descriptor help from `appshell/command_registry.py`
- setup or launcher output in `tools/setup/setup_cli.py` and `tools/launcher/launch.py`
- negotiation and validation reports in `compat/capability_negotiation.py` and `validation/validation_engine.py`

These are useful integration surfaces.
They are not the canonical profile truth.

### Profile References

Profile references are stable identifiers or links that point to a canonical capability-bearing profile without copying its meaning inline.

The live repo already uses this pattern heavily:

- `product_id`
- `platform_id`
- `tool_id`
- `server_profile_id`
- `law_profile_id`
- `access_policy_id`
- `securex_policy_id`

Portable now:

- the idea that a capability profile can be referenced by stable id
- the idea that tasks, evidence, and permissions may link to those ids

Not portable now:

- the exact Dominium id namespaces
- the exact registry roots that own those ids

### Profile Bundles or Compositions

A capability profile can be a bundle or composition that packages several declarations together without becoming a runtime engine.

The live repo already proves this shape through:

- product defaults that combine feature, required, optional, protocol, contract-range, and degrade-ladder declarations in `data/registries/product_capability_defaults.json`
- law profiles that combine grants, revocations, entitlements, intent family limits, and refusal codes in `data/registries/law_profiles.json`
- server profiles that combine replication, anti-cheat, SecureX, law, and entitlement posture in `data/registries/server_profile_registry.json`

Portable now:

- the concept of a named capability-bearing bundle or profile composition
- the concept that such a profile can carry included, conditional, and excluded declarations together

Not portable now:

- exact runtime composition order
- exact fallback precedence
- exact activation rules in launcher, setup, session, or loopback flows

### Portable Capability Profiles Versus Dominium-Retained Profile Families

Portable now:

- the declarative shape shared by product, platform, tool, and mixed governance-bearing profile rows
- the fact that profile declarations may expose support, dependency, exclusion, and compatibility posture

Dominium-retained now:

- exact profile vocabularies such as `cap.*`, `platform.*`, `law.*`, `server.profile.*`, `contract.*`, and `protocol.*`
- platform probing and feature projection
- exact launcher, AppShell, server, and session activation behavior
- profile families whose current semantics are tightly product-bound, such as compute, lens, topology, partition, realism, and universe-physics profiles

## C. Portable Capability-Profile Fields

Every portable capability profile must specify the following fields.

| Field | Requirement | Meaning |
| --- | --- | --- |
| `profile_id` | required | Stable canonical profile identifier. It must survive UI, CLI, wrapper, or registry-layout changes. |
| `profile_kind` | required | Stable category of capability profile, such as product defaults, platform matrix, tool capability profile, or mixed governance profile. This is not a runtime mode string. |
| `declared_capability_classes` | required | Canonical capability classes or capability-family tokens the profile declares. Each declaration must be classifiable as supported, conditionally supported, or excluded. |
| `capability_constraints` | required | Limits, conditions, or gating notes attached to those declarations, including support tier, dependency ceilings, compatibility bounds, or declared fallback eligibility. |
| `required_dependencies` | required | Dependencies that must hold for the profile to be lawfully usable, such as protocol ranges, contract categories, entitlement gates, policy ids, or artifact requirements. |
| `optional_dependencies` | conditional | Dependencies that refine or expand the profile without invalidating it when absent. |
| `policy_permission_links` | required | Policy or permission references that govern whether declared capabilities may actually be exercised. This may be empty, but the field must exist explicitly. |
| `task_suitability` | required | Task kinds, task constraints, or suitability notes that describe what the profile can lawfully support. |
| `task_exclusions` | required | Explicit task, action, or capability usages the profile excludes or forbids. |
| `evidence_review_links` | conditional | Evidence or review references required to trust, elevate, or validate profile claims or exceptions. |
| `profile_source_refs` | conditional | Stable references to the canonical registry, manifest, or profile rows that define the declaration. |
| `compatibility_notes` | required | Contract-range, protocol-range, refusal-on-mismatch, forward-compatibility, or ignore-unknown expectations for the profile shape itself. |
| `portability_limits` | required | Repo-local assumptions, retained bindings, or runtime/product dependencies that still bound portability. |
| `version_notes` | required | Version or schema expectations for the profile and its declared compatibility surface. |
| `stability` | required | Current stability class and the threshold for changing the shape later. |

Operational rule:

- these fields freeze portable profile truth
- runtime-only fields such as selected platform, selected mode, compatibility mode, degrade plan, attach decision, read-only activation, process supervision state, or workspace routing remain outside the portable capability-profile contract

## D. Required Boundary Distinctions

The following distinctions are mandatory and may not be flattened.

### Capability Profile vs Runtime Capability Resolution

- capability profile declares supported, conditional, excluded, and dependency-bound capability posture
- runtime capability resolution decides what actually activates on a concrete host, peer, or session
- probing, negotiation, and degrade execution belong to runtime resolution

### Profile Declaration vs Profile Activation

- profile declaration is the canonical row or bundle that says what may be supported
- profile activation is the concrete use of that declaration in a launcher, setup, AppShell, session, or server path

### Profile Compatibility vs Permission Grant

- compatibility says whether a declared profile can interoperate or coexist with another declaration or host context
- permission says whether an authority context may exercise an action or capability under governing policy
- a compatible profile is not automatically permitted

### Profile Support vs Implementation Completeness

- declared support means the repo has a canonical declaration for a capability class or profile row
- implementation completeness means the repo has fully working runtime behavior for that declaration across current targets
- the live repo explicitly proves these can diverge through provisional rows, future stubs, and degrade or read-only outcomes

### Canonical Profile vs UI or CLI Summaries

- canonical truth lives in the profile row or equivalent contract-bearing declaration
- UI selectors, help text, compatibility reports, or dashboards are derived views
- derived views may summarize or filter, but may not redefine canonical profile truth

## E. Interaction With Prior Portable Contracts

Capability profiles must align with the prior portable contracts without collapsing into them.

### Linkage to the Portable Task Contract

- a task contract may declare required capabilities, optional capabilities, suitability expectations, exclusions, or portability limits
- a capability profile supplies the declaration-side posture those task hooks can reference
- a capability profile does not create, schedule, or execute a task

### Linkage to the Evidence and Review Contract

- a capability profile may require evidence or review linkage when profile claims depend on trust, validation, negotiation, or exception handling
- compatibility reports, negotiation records, and validation findings are derived evidence about applying a profile
- those records are not the canonical profile itself

### Linkage to the Policy and Permission Shape

- a capability profile may carry policy or permission references such as `access_policy_id`, `securex_policy_id`, or other governing ids
- those links express dependency and interpretation boundaries
- they do not themselves grant or deny use

### Runtime Linkage That Stays Out of Scope

- runtime resolution of profile conflicts
- activation order and fallback selection
- host probing and platform filtering
- queueing, scheduling, or adapter transport
- persistent registry services or distributed profile publication

Those are real later-AIDE or Dominium-runtime topics, but they are not part of this portable shape.

## F. Repo-Grounded Rationale

This contract freeze is based on live repo evidence rather than aspiration.

- `data/registries/product_capability_defaults.json` proves that canonical profile rows already carry `feature_capabilities`, `required_capabilities`, `optional_capabilities`, `protocol_versions_supported`, `semantic_contract_versions_supported`, `degrade_ladders`, and `stability`. That directly supports `declared_capability_classes`, `required_dependencies`, `optional_dependencies`, `compatibility_notes`, `version_notes`, and `stability`.
- `data/registries/platform_capability_registry.json` proves that platform rows already carry `platform_id`, `support_tier`, and explicit capability booleans. That is the repo-grounded reason to freeze support, conditional support, exclusion, and capability constraints separately from runtime activation.
- `data/registries/tool_capability_registry.json` proves that capability-bearing rows can carry `capability_kind`, `required_entitlement_id`, `access_policy_id`, and allowed-process metadata. That supports `profile_kind`, `policy_permission_links`, `task_suitability`, and dependency fields.
- `data/registries/capability_registry.json` proves that capability classes already have stable ids, descriptions, and stability markers, while many remain provisional. That is the repo-grounded reason to freeze capability-class references without claiming implementation completeness.
- `data/registries/law_profiles.json` and `data/registries/server_profile_registry.json` prove that named profiles can bundle grants, revocations, entitlements, allowed or forbidden law posture, and refusal-bearing governance links. That supports bundle or composition semantics and explicit exclusions, while also showing why many such rows remain Dominium-retained.
- `compat/descriptor/descriptor_engine.py` proves that endpoint descriptors are derived from canonical product defaults plus platform projection. That is the repo-grounded reason to keep canonical profile truth separate from descriptor emission and host-specific projection.
- `compat/capability_negotiation.py` proves that runtime compatibility outcomes such as `compat.full`, `compat.degraded`, `compat.read_only`, and `compat.refuse` are derived from applying declarations, dependencies, and degrade ladders. That is the repo-grounded reason to exclude runtime resolution semantics from the portable profile shape.
- `appshell/ui_mode_selector.py` proves that explicit fallback from rendered mode to TUI or refusal is a deterministic selection result driven by runtime availability and fallback maps. That is derived activation state, not canonical profile truth.
- `appshell/command_registry.py`, `tools/launcher/launch.py`, and `tools/setup/setup_cli.py` prove that command surfaces package integration behavior, install/update defaults, trust wiring, and activation flow around deeper profile declarations. That is why command surfaces stay outside the portable profile contract.
- `validation/validation_engine.py` proves that negotiation and validation suites consume descriptors and negotiation records as evidence-bearing outputs. That supports explicit evidence/review linkage while keeping those reports derived.
- `tools/xstack/testx/tests/test_required_cap_mismatch_refuses.py` proves that required-capability mismatches are a first-class refusal shape.
- `tools/xstack/testx/tests/test_unknown_cap_ignored.py` proves that unknown future capability tokens can be ignored deterministically rather than silently promoted into support.
- `tools/xstack/testx/tests/test_cross_platform_caps_degrade_consistent.py` proves that conditional support and degrade outcomes are explicit and deterministic across platforms.

The portable minimum is therefore justified by implementation patterns already present in Dominium, while runtime resolution and product-shell activation remain intentionally excluded.

## G. What Is Portable Now vs Not Portable Now

### Portable Now

The following capability-profile elements can be frozen as portable now:

- stable profile identity and profile kind
- declared capability classes
- support, conditional-support, exclusion, and dependency-bound posture
- required and optional dependencies
- compatibility ranges and compatibility notes
- task suitability and task exclusions
- policy and permission linkage
- evidence and review linkage when explicitly declared
- source references, portability limits, version notes, and stability markers
- the idea of named profile bundles or compositions

### Dominium-Retained Now

The following remain Dominium-retained and must not be frozen as portable capability-profile truth now:

- exact Dominium vocabularies such as `cap.*`, `platform.*`, `law.*`, `server.profile.*`, `protocol.*`, and `contract.*`
- concrete product, platform, tool, law, and server profile registries as ownership roots
- platform probing and capability projection in `engine.platform.*` and descriptor emission
- runtime compatibility modes, degrade-plan execution, and read-only override behavior
- AppShell mode selection, command gating, launcher attach decisions, and setup activation defaults
- server, loopback, and session selection of law, server, physics, realism, lens, topology, partition, and other runtime profiles
- install, update, trust, and release profile defaults

### Deferred Until After the Playable Baseline

The following are plausible later AIDE topics but remain deferred now:

- a portable runtime capability resolver
- adapter publication and adapter-claim contracts
- distributed or cross-repo capability discovery
- automatic profile composition and conflict-solving services
- queue, daemon, or scheduler interaction with capability claims
- capability registry services, remote publication, or live subscription models

## H. Capability Inclusion, Exclusion, and Conflict Model

The portable model must keep the following distinctions explicit.

### Supported Capability

A capability class is declared by the profile and has no declared blocking dependency or exclusion inside the profile contract.

### Conditionally Supported Capability

A capability class is declared, but only under explicit dependencies, compatibility bounds, policy posture, host constraints, or fallback-aware limits.

### Excluded Capability

A capability class is explicitly absent, revoked, forbidden, or outside the intended scope of the profile.

### Blocked Capability

A capability class is declared, but current policy, evidence, review, compatibility, or authority state prevents lawful activation in the current context.

### Conflicting Capability

Two declarations, dependencies, or profile bundles collide in a way that cannot be treated as jointly active without explicit higher-order resolution.

### Profile Mismatch

A requested or supplied profile posture does not satisfy the required profile posture for the peer, task, host, or governed context.

### Profile Ambiguity

The available canonical declarations do not provide one unambiguous interpretation of what profile should apply.

Operational note:

- unknown future capability tokens do not automatically prove support
- the live repo already proves that unknown capability tokens can be ignored deterministically until stronger canon promotes them

## I. Canonical vs Derived Distinctions

Canonical capability-profile truth is:

- the authoritative declaration in a capability-bearing registry row, bundle, default set, or equivalent contract-bearing source
- the declarative basis from which descriptors, selections, reports, and validations are derived

Derived views include:

- endpoint descriptors
- compatibility reports
- degrade plans
- selected mode or selected profile summaries
- launcher or setup status output
- UI or CLI selector cards

Derived surfaces may summarize or apply profile truth.
They may not redefine:

- profile identity
- declared capability classes
- dependency posture
- compatibility posture
- exclusions
- portability limits

## J. Anti-Patterns and Forbidden Shapes

The following moves are forbidden for this series.

- embedding runtime capability-selection or negotiation-engine semantics into the canonical profile shape
- assuming declared capability support means implementation completeness
- treating portability as implied by file location
- collapsing compatibility posture into permission or policy posture
- promoting selected mode, attach state, or negotiation record into canonical profile truth
- treating AppShell or launcher command metadata as the canonical capability profile
- using future adapter-runtime ambitions to overexpand the portable shape
- using this artifact to justify broad refactors, broad renames, or runtime expansion ahead of the playable baseline

## K. Stability and Evolution

Stability class: `stable`.

This artifact is authoritative for the current XStack/AIDE series until an explicit follow-up artifact replaces it.

Later prompts that may consume this artifact include:

- `X-6` adapter-contract extraction or equivalent adapter-boundary mapping
- later extraction reviews that need to relate adapters or execution surfaces back to declared capability posture
- later portability review prompts that need to compare runtime claims against frozen declaration shape

The following changes require explicit follow-up rather than silent drift:

- changing the required field set
- redefining the meaning of supported, conditional, excluded, blocked, or conflicting posture
- reclassifying runtime resolution semantics as portable declaration truth
- promoting concrete Dominium vocabularies or ownership roots into portable canon
- treating profile activation summaries as canonical profile truth
