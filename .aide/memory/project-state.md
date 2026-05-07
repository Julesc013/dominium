# Dominium Project State

## Identity

- target repo: `julesc013/dominium`
- local root: `d:/Projects/Dominium/dominium`
- source pack: `D:/Projects/AIDE/aide/.aide/export/aide-lite-pack-v0`
- import pilot: `Q23-dominium-import-pilot`

## Summary

Dominium / Domino is a deterministic simulation platform and product stack with
explicit authority, data-first architecture, reproducible execution, and a
large doctrine and governance corpus. Repo language describes Dominium as the
product layer on top of the Domino deterministic universe simulation engine,
with engine, game, client, server, packs, schemas, and XStack governance
surfaces.

## Current Pilot

The current pilot imports AIDE Lite into Dominium and proves that compact,
doctrine-aware task packets can carry enough constraints for future Codex work
without pasting whole doctrine files or long chat history into prompts.

## Immediate Goal

Generate a compact doctrine-aware next Dominium task from repo state, then
measure prompt-size reduction against an objective doctrine-heavy baseline.

## Source Of Truth

Full Dominium doctrine remains in repo files, not in this memory file. Use
compact summaries and path references. Canon and governance precedence starts at:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- task-relevant doctrine under `docs/planning/**`, `specs/reality/**`,
  `data/reality/**`, `schema/**`, and `docs/contracts/**`

## Doctrine Reference Rule

Reference doctrine by path and brief invariant labels. Do not inline whole
doctrine files into memory, packets, evidence, or future prompts. If a task
needs more precision, load the relevant file directly from the repo.

## Current Constraints

- Extend over replace.
- Preserve determinism, Process-only mutation, law-gated authority, and
  truth / perceived / render separation.
- Keep pack-driven integration and explicit refusal/degradation behavior.
- Respect ownership splits: `fields/` over `field/`; `schema/` over
  `schemas/`; scoped `packs/` versus `data/packs/`; `specs/reality/` over
  `data/reality/`; `docs/planning/` over `data/planning/`.
- Treat generated artifacts as evidence only unless explicitly promoted.

## Deferred Surfaces

- Dominium product features and simulation/model changes.
- Engine, runtime, client, server, and product implementation changes.
- Governance, canon, glossary, or constitutional rewrites.
- Gateway/provider work, live routing, provider calls, local model setup, MCP,
  A2A, UI, autonomous loops, semantic cache, vector DB, exact tokenizer, and
  provider billing integration.

## Token Rule

Use `.aide/context/latest-task-packet.md` as the compact task brief after Q23.
Do not paste long chat history, whole doctrine files, whole repo dumps, raw
prompts, raw responses, provider keys, or `.aide.local/` contents.

## Validation Baseline

Q23 validation records AIDE Lite doctor, validate, snapshot, index, context,
pack, estimate, verifier/review/eval commands where available, `git diff
--check`, `git check-ignore .aide.local/`, JSON parsing for touched generated
JSON, and targeted secret scanning.

Dominium product FAST validation is considered separately because pre-existing
uncommitted FAST validation report artifacts were present before Q23 and must
not be overwritten as part of the import pilot.

## Next Intended Task

Use the generated compact packet to select one bounded Dominium follow-up that
improves AIDE Lite doctrine coverage or task-packet quality without modifying
Dominium product code.
