Status: CANONICAL
Last Reviewed: 2026-04-06
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: domain constitution run
Replacement Target: later bridge-instance checkpoints may refine domain-specific content without replacing this template floor
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`, `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`, `specs/reality/SPEC_CAPABILITY_SURFACES.md`, `specs/reality/SPEC_FORMALIZATION_CHAIN.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `docs/planning/UNIVERSAL_DOMAIN_CONSTITUTION_TEMPLATE.md`

# Cross-Domain Bridge Template

## A. Purpose And Scope

This artifact is `POST-ZETA-3`.

It freezes the reusable lawful bridge template every future bridge constitution or bridge section must follow.

It extends `SPEC_CROSS_DOMAIN_BRIDGES`.
It does not replace it.

## B. Mandatory Bridge Template Sections

Every bridge declaration must contain all of the following:

### B.1 Bridge Identity

Must declare:

- `bridge_id`
- title and summary
- bridge purpose
- bridge class
- directionality

### B.2 Domain Ownership And Boundary

Must declare:

- source domain
- target domain
- canonical ownership roots
- overlap or quarantine notes
- what the bridge does not authorize

### B.3 Allowed Dependency Direction

Must declare:

- one-way, symmetric, mediated, anchor-to-many, or asymmetric bidirectional posture
- what dependency direction is forbidden
- which side may constrain, inform, or refuse the other

### B.4 Data, Control, And Authority Surface

Must declare:

- data exchanged or interpreted
- control surfaces touched
- authority or jurisdiction surfaces touched
- whether the bridge is observational, causal, institutional, persistence-bearing, or mixed

### B.5 Preserved Invariants

Must declare:

- identity and provenance invariants
- topology or connectivity invariants where relevant
- conservation or boundedness invariants where relevant
- institutional or authority invariants where relevant

### B.6 Semantic Leakage Risks

Must declare:

- likely ownership leakage risks
- likely projection-versus-canon confusion risks
- likely runtime convenience overclaim risks

### B.7 Failure And Refusal Modes

Must declare:

- blocked states
- degraded states
- invalid or unsafe states
- authority or jurisdiction refusals
- missing formalization or compatibility refusals

### B.8 Verification Hooks

Must declare:

- invariant checks
- evidence classes
- audit hooks
- replay or provenance hooks where relevant
- review gates if human review remains required

### B.9 Compatibility And Stability Notes

Must declare:

- stability class
- replacement target if provisional
- compatibility notes
- downstream dependencies

## C. Required Bridge Drafting Rules

Every bridge declaration must also:

- preserve canonical domain ownership
- refuse projection promotion by convenience
- distinguish data flow from authority transfer
- distinguish observational coupling from mutation authority
- record macro and micro continuity expectations if scale matters

## D. Anti-Patterns

The following are forbidden:

- bridge purpose defined only by shared code adjacency
- authority transfer inferred from data flow
- one domain silently absorbing another domain's ownership
- UI or runtime service boundaries treated as bridge law
- bridge validity inferred from implementation presence alone
- missing failure or refusal semantics

## E. Template Outcome

The reusable cross-domain bridge floor is now frozen.

Future domain constitutions may specialize this template per bridge instance, but they may not discard its ownership, failure, verification, or anti-leakage discipline.
