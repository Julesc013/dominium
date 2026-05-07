# Doctrine Context Report

Major doctrine/governance/architecture docs discovered:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `CLAUDE.md`
- `docs/README.md`
- `docs/ARCHITECTURE.md`
- `docs/XSTACK.md`
- `docs/STATUS_NOW.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `docs/planning/POST_PI_EXECUTION_PLAN.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
- `specs/reality/*.md`
- `data/reality/*.json`
- `docs/xstack/AIDE_*.md`

Referenced by packet/context:

- `.aide/context/latest-task-packet.md` directly references
  `.aide/context/dominium-doctrine-refs.md`, canon, glossary, `AGENTS.md`,
  planning authority/intake/state/ledger/gates/ownership/desire docs,
  `specs/reality/`, and `data/reality/`.
- `.aide/context/dominium-doctrine-refs.md` gives compact path summaries for
  the doctrine floor.
- `.aide/context/repo-map.*` and `.aide/context/context-index.json` provide
  metadata refs only.

Intentionally not inlined:

- Canon, glossary, planning docs, `specs/reality/**`, `data/reality/**`, XStack
  AIDE docs, product source, generated reports, and prior chat text.

Project-state compactness:

- `.aide/memory/project-state.md` is about 905 approx tokens.
- It records current actionable state, source-of-truth path refs, token rules,
  deferrals, and next task. It does not dump doctrine.

Key constraints preserved as refs:

- authority precedence and repo truth over chat memory
- determinism, Process-only mutation, law-gated authority, profile composition
- truth / perceived / render separation
- pack-driven integration and explicit refusal/degradation
- schema/pack/field/reality/planning ownership splits
- generated artifacts as evidence only
- review gates for protected or ownership-sensitive work

Coverage gaps:

- The compact packet does not enumerate every architecture doc under
  `docs/architecture/**`.
- Domain-specific implementation docs are discovered in the repo map but need
  manual selection for serious domain work.
- Pack/schema details may require task-specific curation before implementation.

Recommendation:

- Establish Dominium-specific golden tasks for governance-only work, schema
  projection work, domain-contract work, and runtime-boundary work before using
  AIDE broadly for implementation.
