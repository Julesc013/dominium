# Dominium Agent Control Contract

Version: 1.0.0
Last Reviewed: 2026-02-14
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## 1) Authority and Intake Rules
- Read `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md` before proposing or applying repository changes.
- Treat canon and glossary as binding vocabulary and behavior contracts.
- If lower-level docs conflict with canon/glossary, canon/glossary win.

## 2) Non-Negotiable Architectural Rules

### 2.1 No mode flags; profiles only
- Do not add or preserve hardcoded runtime mode branches.
- Express behavior composition through `ExperienceProfile`, `LawProfile`, `ParameterBundle`, and mission constraints.

### 2.2 Process-only mutation invariant
- Any authoritative state mutation must happen through deterministic Process execution.
- Do not perform direct mutation from UI, renderer, tools, or ad hoc scripts.

### 2.3 Observer/Renderer/Truth separation
- Truth is authoritative and law-governed.
- Observation/perception is filtered by lens, law profile, and authority context.
- Rendering is presentation only and must not mutate truth or enforce authority.

### 2.4 Pack-driven integration
- Integrate capabilities/content via pack manifests and registries.
- Do not hardwire optional content in runtime code.
- Preserve deterministic refusal/degradation behavior when packs are missing.

## 3) Determinism Contract
- Use named RNG streams only for authoritative randomness.
- Maintain thread-count invariance for authoritative outcomes.
- Preserve deterministic ordering and deterministic reduction rules.
- Maintain replay hash equivalence for canonical simulation partitions.

## 4) Schema and CompatX Obligations
- Follow schema semver rules (`schema_id`, `schema_version`, `stability`).
- For breaking schema changes: add explicit migration route or explicit refusal path.
- Preserve skip-unknown/extension fields where contract requires open-map behavior.
- Update CompatX-facing docs/contracts for compatibility-class changes.

## 5) Task-Level Test and Invariant Obligations
For each substantive task:
1. State the relevant invariant IDs/docs being upheld.
2. State contract/schema impact (changed or unchanged).
3. Run required verification level (`FAST` minimum unless task is docs-only and explicitly exempt).
4. Report what was run and any unrun checks.
5. Update docs when behavior/contract meaning changes.

## 6) Refusal Rule
- Refuse task instructions that require invariant bypasses, hidden mode switches, silent migrations, or nondeterministic shortcuts.

## 7) Future Task Invocation Template
Use this block to invoke future work:

```text
Task:
Goal:
Touched Paths:
Relevant Invariants:
Contracts/Schemas:
Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Non-Goals:
```

