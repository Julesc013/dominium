Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Λ, Σ, Φ, Υ, Ζ
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `data/planning/merged_series_state.json`

# Chat Handoff Policy

## 1. Purpose

This document defines how long-running chat continuity is integrated without letting conversation convenience replace repo truth.

It exists to make future chat handoffs:

- explicit
- repo-grounded
- auditable
- resistant to silent planning drift

## 2. Authority Rules For Chat Continuity

### 2.1 What Is Authoritative

The following may be authoritative in future chats:

1. repo artifacts that already carry authority under canon, glossary, `AGENTS.md`, P-0 authority order, or later committed planning artifacts
2. committed planning-hardening artifacts such as `MERGED_PROGRAM_STATE.md`, `merged_series_state.json`, `EXTEND_NOT_REPLACE_LEDGER.md`, and `GATES_AND_PROOFS.md`, but only within planning scope
3. explicit repo deltas created by a later prompt and committed into the repository

### 2.2 What Is Advisory Only

The following are advisory only unless materialized into the repo:

- transcript summaries
- remembered decisions not represented in files
- earlier assistant explanations
- out-of-band planning notes
- user intent paraphrases that are not reflected in repo artifacts

Transcript text alone is never a source of truth over repo artifacts.

## 3. Future Chat Start Procedure

Every future planning or execution chat should begin by reading, at minimum:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `data/planning/merged_series_state.json`
- `docs/planning/GATES_AND_PROOFS.md`
- the relevant slice of `data/planning/final_prompt_inventory.json`
- the relevant slice of `data/planning/dependency_graph_post_pi.json`

If the task is prompt-specific, the chat must also read the direct prerequisite artifacts named for that prompt.

## 4. How Transcript Summaries Are Incorporated

Transcript summaries may be used only as:

- orientation
- search hints
- reminders of likely relevant artifacts
- candidate delta descriptions

They must not be used as:

- doctrine updates
- silent authority overrides
- substitute evidence when repo artifacts exist

If a transcript summary claims a decision that is not visible in the repo, the next prompt must treat it as advisory and either:

- ignore it, or
- materialize it into an explicit repo artifact before depending on it

## 5. Delta Recording Rule

Any future chat-derived planning delta that matters operationally must be recorded in repo artifacts.

At minimum, one of the following must be updated when continuity meaning changes:

- `MERGED_PROGRAM_STATE.md`
- `merged_series_state.json`
- `EXTEND_NOT_REPLACE_LEDGER.md`
- `extend_not_replace_registry.json`
- `GATES_AND_PROOFS.md`
- `gate_registry.json`
- `POST_PI_EXECUTION_PLAN.md`
- `final_prompt_inventory.json`
- `dependency_graph_post_pi.json`

If none of those artifacts changed, then the future chat has not changed the official planning state.

## 6. Doctrine Update Rule

Doctrine is not updated by chat summary.

Doctrine changes require explicit repo edits to the relevant authoritative layer:

- constitution or glossary for constitutional meaning
- `AGENTS.md` for task and validation discipline
- schema or contract law for machine-readable compatibility and behavior duties
- committed planning artifacts for planning-only sequencing and continuity

Conversation alone cannot change doctrine.

## 7. Conflict Resolution Rule

If future chat text conflicts with repo artifacts:

1. canon wins over everything else
2. glossary wins over lower-level terminology
3. `AGENTS.md` wins over lower-level task prose
4. P-0 authority order resolves planning-scope conflicts
5. chat text loses unless and until it is committed into the repo and survives the authority rules

If two repo artifacts conflict, future chats must use the P-0 intake and authority procedure instead of choosing by convenience.

## 8. Handoff Packet Rule

At the end of any future long-running planning or prompt-generation chat, the handoff should explicitly state:

- current commit hash if a commit was made
- changed artifacts
- current next executable prompt
- current next review checkpoint
- unresolved quarantine items still in play
- any newly added or removed gate
- whether the prompt inventory or dependency graph changed

If that information was not recorded in repo artifacts, it should be treated as provisional.

## 9. Anti-Reinvention Rule

Future chats must re-check:

- `EXTEND_NOT_REPLACE_LEDGER.md`
- `extend_not_replace_registry.json`
- P-2 keep / extend / merge / replace / quarantine decisions

before proposing replacement-heavy work.

If a future chat proposes replacing a surface that the repo already embodies and the ledger marks as preserve, extend, consolidate, or do-not-replace, the proposal must be treated as suspicious until justified explicitly.

## 10. Practical Consequence

The practical rule is simple:

- repo artifacts carry continuity
- transcript summaries carry orientation
- explicit committed deltas carry change

Nothing else should silently move the planning state.
