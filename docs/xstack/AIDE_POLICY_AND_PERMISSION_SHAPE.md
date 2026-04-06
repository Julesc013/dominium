Status: CANONICAL
Last Reviewed: 2026-04-07
Supersedes: none
Superseded By: none
Stability: stable
Future Series: X-5, AIDE extraction review
Replacement Target: later explicit portable policy and permission checkpoint or replacement artifact only
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/xstack/XSTACK_SCOPE_FREEZE.md`, `data/xstack/xstack_scope_freeze.json`, `docs/xstack/XSTACK_INVENTORY_AND_CLASSIFICATION.md`, `data/xstack/xstack_inventory_and_classification.json`, `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`, `data/xstack/aide_portable_task_contract.json`, `docs/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`, `data/xstack/aide_evidence_and_review_contract.json`, `data/xstack/gate_definitions.json`, `data/registries/control_policy_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/securex_policy_registry.json`, `data/registries/access_policy_registry.json`, `data/registries/tool_capability_registry.json`, `data/registries/role_registry.json`, `data/registries/security_roles.json`, `data/registries/law_profiles.json`, `data/registries/controlx_policy.json`, `data/registries/refusal_code_registry.json`, `data/registries/refusal_to_exit_registry.json`, `tools/xstack/registry_compile/compiler.py`, `tools/xstack/securex/check.py`, `security/trust/trust_verifier.py`, `appshell/command_registry.py`, `appshell/commands/command_engine.py`, `appshell/pack_verifier_adapter.py`, `tools/xstack/sessionx/pipeline_contract.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `server/server_boot.py`, `server/net/loopback_transport.py`, `client/interaction/affordance_generator.py`

# AIDE Policy and Permission Shape

## A. Purpose and Scope

This artifact freezes the canonical portable policy and permission shape that later XStack/AIDE prompts may reuse.

It exists because:

- `X-0` froze what XStack means now and what remains outside the current series
- `X-1` classified which live surfaces are portable core, ops, runtime, Dominium-retained, legacy, or mixed
- `X-2` froze the portable task unit and required explicit permission and policy hooks
- `X-3` froze portable evidence and review, which policy and permission decisions must link back to when they matter
- later extraction work still needs a smaller and stricter contract for policy declaration and permission posture itself

This artifact solves a specific narrowing problem:

- the live repo already has policy registries, trust and securex rules, law profiles, access policies, role and entitlement grants, refusal code families, gate profiles, provisional allowances, and permission-bearing affordance rows
- later AIDE work needs the portable minimum those surfaces imply
- that portable minimum must be frozen without smuggling in authorization services, daemons, schedulers, workflow engines, or product-shell runtime behavior

This artifact governs:

- what portable policy means in the live XStack/AIDE sense
- what portable permission means in the live XStack/AIDE sense
- which fields every canonical portable policy or permission shape must expose
- which boundaries must remain explicit
- which parts are portable now versus Dominium-retained now versus deferred until after the playable baseline exists
- which later prompts may treat this artifact as their fact base

This artifact is downstream of `X-0`, `X-1`, `X-2`, and `X-3`.
It does not reopen scope, inventory, task, or evidence/review classification.
It narrows those earlier artifacts into portable policy and permission truth only.

This artifact must preserve current repo reality:

- admissible `Zeta` doctrine and gating work is complete
- the immediate product priority remains the canonical repo-local playable baseline and repo stabilization
- XStack/AIDE work must support clarification, modularization, and contract extraction without competing with the baseline path

This artifact is a contract freeze.
It does not implement a policy engine, authorization service, daemon, scheduler, queue, adapter layer, compiler, or broader AIDE runtime.

## B. Current-State Definition of Portable Policy

Current definition:

Portable policy is a canonical declarative rule surface that states which subject classes may attempt which action, capability, artifact, or operation classes under which condition or gate classes, what decision classes are allowed, what escalation or override posture exists, and what evidence or review links constrain interpretation, without embedding runtime enforcement, product-shell dispatch, storage layout, or repo-local operator workflow.

Portable policy is portable now when it captures the minimum truth needed for another XStack/AIDE consumer to understand:

- what rule surface is being declared
- what kind of subjects or governed objects it applies to
- what actions, capabilities, or artifact classes it governs
- what gates or conditions must hold
- what decision classes can result
- what escalation or override classes are explicitly allowed
- what portability limits still bind the rule surface

The portable policy model must distinguish the following.

### Canonical Policy

Canonical policy is the authoritative declarative rule surface a governed consumer may rely on directly.

In the live repo, canonical policy is already implied by registry-backed policy rows and other contract-bearing declarative surfaces such as:

- `data/registries/control_policy_registry.json`
- `data/registries/trust_policy_registry.json`
- `data/registries/securex_policy_registry.json`
- `data/registries/access_policy_registry.json`
- `data/xstack/gate_definitions.json`
- `data/registries/controlx_policy.json`
- `data/registries/law_profiles.json`

Canonical policy is not defined by where a command prints it or whether a UI makes it visible.
It is defined by the governing contract attached to the policy row or profile.

### Derived Policy Views and Summaries

Derived policy views are rendered summaries, command help, setup or launcher status payloads, dashboards, or markdown/operator reports that expose policy meaning without redefining it.

For example, AppShell command descriptors and refusal-to-exit mappings package policy outcomes for shells.
They are useful integration views, but they do not redefine canonical policy law.

### Policy References

Policy references are stable identifiers or links that point to a canonical policy without copying its meaning inline.

The live repo already uses this pattern heavily:

- `trust_policy_id`
- `securex_policy_id`
- `control_policy_id`
- `access_policy_id`
- `law_profile_id`
- `required_anti_cheat_policy_id`
- `allowed_law_profile_ids`

Policy references are portable now.
Concrete registry roots and runtime lookup rules are not.

### Policy Bundles or Profiles

Policy bundles or profiles are named selections that package several rule decisions together without becoming a runtime engine.

The live repo already shows this shape through:

- `FAST`, `STRICT`, and `FULL` gate profiles in `data/xstack/gate_definitions.json`
- `law_profiles.json`, which bundles grants, revocations, allowed and forbidden intents, audit requirements, and refusal codes
- trust policy selection in `security/trust/trust_verifier.py`

Portable now:

- the concept of a named profile or bundle as a stable selection surface
- the fact that profiles package policy posture

Not portable now:

- exact profile wiring into launcher, setup, server boot, or CI
- repo-local defaults, fallback order, or release-specific publication rules

### Portable Policy Versus Dominium-Retained Policy

Portable now:

- policy identity, kind, scope, subject classes, action or capability classes, gate classes, decision classes, escalation classes, and linked evidence or review markers

Dominium-retained now:

- exact policy vocabularies such as `law.*`, `trust.*`, `securex.*`, `ctrl.*`, `entitlement.*`, `cap.*`, and `refusal.*`
- concrete registry ownership and runtime lookup paths
- product-shell routing, exit code packaging, and install defaults

## C. Current-State Definition of Portable Permission

Current definition:

Portable permission is a canonical decision shape or decision-ready linkage that states whether a subject class or authority context may attempt a target action, capability, artifact interaction, or process under applicable policy, what gate conditions and evidence are required, whether the result is granted, conditional, denied, refused, blocked pending review, or escalated, and what override or exception posture exists, without embedding runtime authorization engines, product-shell execution, or queue or workflow semantics.

Portable permission is portable now when it captures the minimum truth needed for another XStack/AIDE consumer to understand:

- what subject or authority context is being evaluated
- what action or capability target is being requested
- what policy basis governs the decision
- what grant, denial, refusal, or conditional posture applies
- what evidence or review is required
- whether escalation or override is possible

The portable permission model must distinguish the following.

### Permission Requirement

A permission requirement is the set of gates that must already hold before a grant can exist.

The live repo already uses this shape through:

- required entitlements and privilege levels in `data/registries/access_policy_registry.json`
- `required_entitlement_id` and `access_policy_id` in `data/registries/tool_capability_registry.json`
- granted and revoked capabilities, allowed and forbidden intent families, and `audit_required` in `data/registries/law_profiles.json`
- missing entitlements and missing lens channels in `client/interaction/affordance_generator.py`

### Permission Grant Posture

Grant posture records whether a request is allowed and whether it is unrestricted or conditional.

The live repo shows this through:

- enabled affordance rows in `client/interaction/affordance_generator.py`
- trust results that complete with warnings or bridge allowances in `security/trust/trust_verifier.py`
- declared allowances in `data/xstack/gate_definitions.json`

### Permission Denial and Refusal Posture

Denial posture means the applicable policy exists and resolves negatively.
Refusal posture means the request cannot lawfully proceed because required policy, evidence, compatibility, or authority context is missing, invalid, or outside supported bounds.

The live repo packages many hard negatives through refusal codes, so the portable contract must keep the semantic distinction explicit even when a product shell reports them with a single refusal namespace.

### Escalation and Override Posture

Escalation posture means the current authority or review level is insufficient and stronger review or narrower handling is required.
Override posture means the repo has an explicit and narrow exception path rather than an implicit bypass.

The live repo already shows explicit exception or override-like shapes through:

- `meta_allowed` in `data/registries/control_policy_registry.json`
- signed-bridge handling in `security/trust/trust_verifier.py`
- `allow_read_only` and `law_profile_id_override` in loopback and server boot paths
- semantic escalation keywords in `data/registries/controlx_policy.json`

Portable now:

- explicit escalation and override notation

Dominium-retained now:

- the concrete runtime mechanics that carry those overrides out

### Portable Permission Versus Dominium-Retained Permission

Portable now:

- permission subject and target
- policy basis reference
- grant, refusal, denial, conditional, blocked, and escalated posture
- evidence and review requirements
- override or exception notes

Dominium-retained now:

- exact actor identity resolution
- runtime attach and supervisor mechanics
- product-shell flags such as read-only fallbacks and command-line overrides
- install- and release-specific defaults

## D. Portable Policy Shape Fields

Every portable policy shape must specify the following fields.

| Field | Requirement | Meaning |
| --- | --- | --- |
| `policy_id` | required | Stable canonical policy identifier. It must survive rendering, relocation, or wrapper changes. |
| `policy_kind` | required | Stable policy category such as trust, securex, control, access, gate, law-profile, or review-sensitive governance policy. |
| `policy_scope` | required | The bounded domain where the policy applies, such as artifact kinds, operation categories, product contexts, profiles, or intent families. |
| `subject_classes` | required | Subject or governed object classes the policy applies to, such as roles, privilege tiers, products, artifact classes, or authority contexts. |
| `action_classes` | required | Actions, capabilities, processes, artifact interactions, or operation classes governed by the policy. |
| `condition_or_gate_classes` | required | Required entitlements, signature states, privilege levels, physical access requirements, invariant gates, profile selectors, or other gate classes that constrain decisions. |
| `decision_classes` | required | The allowed decision categories the policy can produce, such as allow, allow-with-conditions, warn, deny, refuse, or degrade. |
| `escalation_classes` | required | Conditions that require stronger review, explicit override, ambiguity resolution, or higher authority. |
| `review_links` | conditional | Review requirements or review references when the policy itself triggers or depends on review. |
| `evidence_links` | conditional | Evidence requirements or evidence references when the policy depends on trust, validation, compat, or review-bearing evidence. |
| `policy_source_refs` | conditional | Stable source references to the canonical registry, manifest, or profile bundle that defines the policy. |
| `portability_limits` | required | Repo-local assumptions, coupled roots, or product/runtime dependencies that still limit portability. |
| `compatibility_notes` | required | Version, schema, refusal-on-unknown, and compatibility expectations for the policy shape itself. |
| `stability` | required | Current stability class and the threshold for future change. |

Operational notes:

- `condition_or_gate_classes` is required because the live repo already models gating through entitlements, privilege levels, signature status, profile ids, required policies, and validation gates
- `decision_classes` is required because live policy surfaces already distinguish allow, warn, refuse, required profile, required policy, and provisional allowance posture
- `policy_source_refs` is conditional because some policy shapes are standalone rows while others are selected through profile or registry references

## E. Portable Permission Shape Fields

Every portable permission shape must specify the following fields.

| Field | Requirement | Meaning |
| --- | --- | --- |
| `permission_id` | required | Stable canonical permission identifier or stable decision identifier. |
| `policy_basis_refs` | required | Stable references to the governing policy rows, profiles, or bundles used to evaluate this permission posture. |
| `permission_subject` | required | The subject or authority context being evaluated, expressed as a class or stable subject reference rather than a shell-specific process handle. |
| `action_or_capability_target` | required | The requested action, capability, process, artifact interaction, or operation target. |
| `grant_posture` | required | Whether the subject is allowed, allowed with conditions, or not granted. |
| `refusal_posture` | required | Whether initiation must be refused because inputs, policy, evidence, compatibility, or authority context are missing or invalid. |
| `denial_posture` | required | Whether an applicable policy exists and resolves negatively on the subject or target. |
| `gate_conditions` | required | The conditions that must hold for the permission to be granted, such as entitlements, trust status, profile membership, physical access, or valid negotiation. |
| `escalation_or_override_notes` | required | Explicit escalation triggers, override classes, exception posture, or notes that the request is only lawful under stronger review or narrower handling. |
| `review_requirements` | conditional | Review requirements when the permission depends on review rather than autonomous evaluation. |
| `evidence_requirements` | conditional | Required evidence or evidence references when the permission depends on trust, validation, review, or audited state. |
| `portability_limits` | required | Repo-local assumptions, coupled roots, or product/runtime dependencies that still limit portability. |
| `compatibility_notes` | required | Version, schema, refusal-on-unknown, and compatibility expectations for the permission shape itself. |
| `stability` | required | Current stability class and the threshold for future change. |

Operational notes:

- `policy_basis_refs` is required because live permission posture is always attached to some declarative basis such as `access_policy_id`, `law_profile_id`, `trust_policy_id`, or a gate profile
- `grant_posture`, `refusal_posture`, and `denial_posture` are separate because the live repo conflates some negatives into refusal codes while still preserving enough structure to keep the portable contract more explicit
- `escalation_or_override_notes` is required because the live repo already has narrow override-like exceptions and stronger-review triggers that must not become invisible

## F. Required Boundary Distinctions

The following boundaries remain mandatory.

### Policy Versus Permission

Policy is the declarative rule surface.
Permission is the evaluated or evaluation-ready posture for a subject and target under policy.

Policies may exist without a current permission decision.
Permission decisions may not redefine the governing policy.

### Requirement Versus Grant

Requirements are the conditions that must already hold.
Grant is the resulting posture once those conditions and the relevant policy basis are evaluated.

The live repo already separates these through required entitlements, privilege levels, signature requirements, and then later allow, warn, or refuse posture.

### Refusal Versus Denial Versus Escalation

Refusal means the request cannot lawfully proceed because required policy, evidence, compatibility, or context is missing or invalid.
Denial means applicable policy exists and resolves negatively.
Escalation means the current authority or review level is insufficient and stronger handling is required.

### Policy Declaration Versus Runtime Enforcement

Policy declaration lives in canonical policy rows, registries, manifests, and contract-bearing metadata.
Runtime enforcement lives in AppShell command dispatch, launcher/setup behavior, trust verification execution, server attach flow, session gating, and similar implementation paths.

Portable X-4 freezes the declarative shape and the decision posture only.
It does not freeze enforcement daemons or shell routing.

### Review-Linked Permission Versus Autonomous Grant

Some permissions resolve autonomously once declared gates are satisfied.
Others remain blocked pending review or require stronger review to continue.

The portable shape must keep those cases explicit rather than assuming all permissions are automatic.

### Evidence-Bearing Permission Decision Versus Unevidenced Local Convenience

Evidence-bearing permission decisions link to trust reports, validation findings, review evidence, compat records, or audit-bearing state.
Unevidenced local convenience includes shell flags, local toggles, or fallback switches that are not enough to redefine canonical permission law.

The live repo makes this distinction important through trust reports, refusal payloads, and guarded review around evidence reclassification.

## G. Repo-Grounded Rationale

These fields and distinctions are the portable minimum because the live repo already relies on them.

### Policy Registries and Gate Catalogs

- `data/registries/control_policy_registry.json` already declares policy ids, allowed actions, allowed abstraction levels, view policies, fidelity ranges, strictness, and explicit meta-law allowances
- `data/xstack/gate_definitions.json` already declares required profiles, provisional allowances, required invariants, rule ids, and validation gates
- `data/registries/controlx_policy.json` already declares forbidden patterns, allowed operation categories, mutation locality rules, and semantic escalation keywords

These surfaces justify freezing policy identity, scope, action classes, gate classes, decision classes, and escalation classes now.

### Trust, SecureX, and Verification Surfaces

- `data/registries/trust_policy_registry.json` and `security/trust/trust_verifier.py` already model policy ids, required signature conditions, allowed unsigned behavior, untrusted-root behavior, warning posture, refusal posture, and signed-bridge exceptions
- `data/registries/securex_policy_registry.json` and `tools/xstack/registry_compile/compiler.py` already model required signature status, unsigned allowances, allowed publishers, refusal codes, and cross-policy references from server policy rows
- `tools/xstack/securex/check.py` already emits warn-versus-refusal posture based on governed signature status

These surfaces justify freezing condition classes, decision classes, evidence links, and override or exception notation now.

### Access, Roles, Law Profiles, and Capability Surfaces

- `data/registries/access_policy_registry.json` already models required entitlements, privilege levels, and physical-access requirements
- `data/registries/tool_capability_registry.json` already links tool capabilities to required entitlements and `access_policy_id`
- `data/registries/role_registry.json` and `data/registries/security_roles.json` already model granted entitlements, restrictions, and law-profile linkage
- `data/registries/law_profiles.json` already models granted and revoked capabilities, allowed and forbidden intent families, audit requirements, and refusal codes
- `client/interaction/affordance_generator.py` already emits permission-bearing rows with required entitlements, missing entitlements, required lens channels, enabled posture, and disabled reason codes

These surfaces justify freezing permission subject, target, policy basis, gate conditions, grant posture, refusal posture, denial posture, and review or audit linkage now.

### Product-Shell and Refusal Packaging Surfaces

- `appshell/command_registry.py` already records refusal code families, supported modes, product ids, and stability data for command surfaces
- `appshell/commands/command_engine.py` already packages refusal code, reason, remediation hint, nested refusal detail, and exit-code dispatch
- `data/registries/refusal_code_registry.json` and `data/registries/refusal_to_exit_registry.json` already classify refusal families and map them into shell-specific exit behavior
- `appshell/pack_verifier_adapter.py` applies trust policy to pack verification and upgrades shell posture to refused when policy is not met

These surfaces justify freezing refusal and denial semantics while also proving that shell-specific packaging must remain outside the portable contract.

### Session, Launcher, Setup, and Runtime Override Patterns

- `tools/setup/setup_cli.py` and `tools/launcher/launch.py` already expose trust-policy selection and compatibility-bound refusal behavior
- `server/server_boot.py` and `server/net/loopback_transport.py` already expose explicit `law_profile_id_override`, `entitlements_override`, and read-only posture in runtime flows
- `tools/xstack/sessionx/pipeline_contract.py` already refuses when required registries or canonical stage references are missing

These surfaces prove that explicit override or exception posture is real in the repo, but the concrete mechanics remain runtime-owned and therefore stay outside the portable shape.

## H. What Is Portable Now Versus Not Portable Now

### Portable Now

The following policy and permission elements are portable enough to freeze now:

- policy identity, kind, scope, subject classes, action classes, gate classes, decision classes, and escalation classes
- policy references and policy-bundle or profile references as named selection surfaces
- permission subject, target, policy basis, gate conditions, and explicit grant, denial, refusal, conditional, blocked, and escalated posture
- review and evidence linkage for policy or permission decisions
- explicit override or exception notation
- portability limits, compatibility notes, and stability markers
- canonical-versus-derived markers

### Dominium-Retained Now

The following elements remain Dominium-owned or context-specific:

- the concrete policy namespaces and live row vocabularies under `data/registries/**`
- exact policy content for trust, securex, control, law, role, entitlement, and gate registries
- AppShell command dispatch, exit-code mapping, and product-command behavior
- launcher and setup CLI flags, defaults, and install-specific trust-policy resolution
- session, server, and loopback enforcement paths including read-only attach and law-profile override mechanics
- concrete trust-root import, publication, rotation, and revocation handling
- product-specific lens, overlay, channel, and affordance semantics

### Deferred Until After the Playable Baseline

The following elements are intentionally deferred:

- policy engines, authorization services, or long-lived enforcement daemons
- distributed role assignment or multi-tenant permission systems
- remote override and approval services
- cross-repo policy publication and federation
- dynamic policy composition, conflict-solvers, or policy compilers
- runtime orchestration for distributed trust, revocation, or policy rollout
- generalized capability negotiation or profile extraction beyond the shape frozen here

This keeps X-4 aligned with the current playable-baseline priority.
It freezes reusable declaration and decision shape without competing with baseline assembly or repo stabilization.

## I. Refusal, Denial, Review, and Escalation Model

The portable model reuses the following distinctions.

| Class | Meaning |
| --- | --- |
| `not_permitted` | No applicable policy basis grants the subject any lawful path for the requested target or action class. |
| `refused` | The request cannot lawfully proceed because required policy rows, evidence, compatibility records, or authority context are missing or invalid. |
| `denied` | Applicable policy exists and resolves negatively on the subject or target. |
| `blocked_pending_review` | Permission cannot conclude until required review or approval occurs. |
| `escalated` | The current authority or review posture is insufficient and stronger handling is required. |
| `allowed_with_conditions` | Permission is granted only under explicit conditions such as warnings, read-only posture, physical access, or audit requirements. |
| `override_or_exception_path` | A narrow and explicit exception path exists, but it must be declared and evidence-bearing rather than implicit. |
| `policy_ambiguity_or_conflict` | Applicable policy references conflict, are incomplete, or leave the system unable to determine a lawful outcome without escalation or refusal. |

Operational consequences:

- `refused` and `denied` are not interchangeable
- `allowed_with_conditions` is not equivalent to unrestricted grant
- `override_or_exception_path` must never be assumed from convenience flags alone
- `policy_ambiguity_or_conflict` must not be resolved by hidden fallback or best-effort guessing
- when the live repo reports a refusal code for a policy denial, the portable contract still keeps the underlying distinction explicit

## J. Canonical Versus Derived Distinctions

Canonical policy and permission truth means:

- the portable policy and permission shape itself
- declarative policy rows, profiles, or bundles explicitly designated as authoritative by stronger contract-bearing sources
- permission-bearing outputs that authoritatively record policy basis, subject, target, gate conditions, and decision posture

Derived views include:

- command help
- status dashboards
- operator summaries
- markdown reports
- UI cards
- exit-code mapping tables

Derived views may summarize, sort, or package canonical truth.
They may not redefine:

- policy scope
- applicable subject classes
- gate or condition meaning
- grant, refusal, denial, or escalation posture
- override requirements
- portability limits
- evidence or review requirements

Canonical policy or permission truth must not be overridden by convenience summaries, chat memory, or product UI.

## K. Anti-Patterns and Forbidden Shapes

The following shapes are forbidden for this series:

- embedding runtime policy-engine or authorization-daemon semantics into the portable shape
- confusing policy declaration with a permission instance
- assuming portability from file location under `data/registries/` or `tools/xstack/`
- treating shell flags or local convenience toggles as canonical permission law
- collapsing refusal, denial, blocked review, and escalation into one generic failure posture
- promoting command help or status output into canonical policy truth
- overgeneralizing from future AIDE runtime ideas into present contract requirements
- freezing concrete Dominium policy vocabularies as if they were already portable AIDE vocabulary
- using this artifact to justify broad refactors or to compete with canonical playable-baseline work

## L. Stability and Evolution

Stability class: `stable`.

This artifact is the canonical portable policy and permission shape until a later explicit checkpoint replaces it.

Later prompts may consume it for:

- capability profile shape extraction
- portable refusal and override contract refinement
- later AIDE interface mapping for policy-bearing surfaces
- later extraction review of which live Dominium policy and permission surfaces can be wrapped versus retained

The following changes require an explicit follow-up artifact rather than silent drift:

- redefining policy-versus-permission semantics
- collapsing refusal and denial posture
- redefining how override or escalation classes work
- promoting runtime enforcement details into the portable shape
- freezing concrete Dominium policy vocabularies as portable AIDE vocabulary without later extraction review
- broadening this contract into a runtime authorization or policy engine
