# Doctrine Preservation

## Consulted Doctrine Packet

The normal Dominium doctrine packet was consulted by path and metadata/content snippets:

- `docs/canon/constitution_v1.md` - canonical, stable, reviewed 2026-02-14.
- `docs/canon/glossary_v1.md` - canonical, stable, reviewed 2026-02-14.
- `AGENTS.md` - canonical agent governance with AIDE managed sections.
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`.
- `docs/planning/AUTHORITY_ORDER.md`.
- `docs/planning/MERGED_PROGRAM_STATE.md`.
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`.
- `docs/planning/GATES_AND_PROOFS.md`.
- `docs/planning/POST_PI_EXECUTION_PLAN.md`.
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`.
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`.
- `specs/reality/*.md`.
- `data/reality/*.json`.
- `data/planning/final_prompt_inventory.json`.
- `data/planning/dependency_graph_post_pi.json`.

Selected planning/reality JSON files parsed successfully with `ConvertFrom-Json`.

## Governance Surfaces Found

- High-authority root docs: `AGENTS.md`, `README.md`, `GOVERNANCE.md`, `DOMINIUM.md`, `SECURITY.md`, `CONTRIBUTING.md`.
- Canon and planning roots: `docs/canon/**`, `docs/planning/**`, `data/planning/**`.
- Reality doctrine roots: `specs/reality/**`, `data/reality/**`.
- Contract/schema roots: `contracts/**`, `schema/**`, `schemas/**`.
- Release/control/security roots: `docs/release/**`, `repo/release_policy.toml`, `release/**`, `updates/**`, `security/**`.
- XStack/governance roots: `docs/XSTACK.md`, `docs/governance/**`, `docs/audit/**`, `data/registries/**`, `repo/repox/**`, `tools/xstack/**`, `tools/xstack/auditx/**`.

## AGENTS.md Status

- `AGENTS.md` remains unmodified by Q49.
- Existing managed AIDE guidance in `AGENTS.md` is current according to `aide_lite.py validate`.
- Q50 must not replace AGENTS manual content, alter authority order, or rewrite managed sections unless an explicit future task and managed-section compiler require it.

## AIDE Memory Compactness

- `.aide/memory/project-state.md` is compact and stores doctrine references by path.
- `.aide/context/dominium-doctrine-refs.md` is a compact index, not a competing doctrine source.
- Q50 should continue path-reference behavior and must not inline full canon, glossary, planning doctrine, raw prompts, or chat history into AIDE memory or packets.

## Files Q50 Must Never Overwrite Blindly

- `AGENTS.md`.
- `docs/canon/**`.
- `docs/planning/**`.
- `specs/reality/**`.
- `data/reality/**`.
- `data/planning/**`.
- `contracts/**`.
- `schema/**` and `schemas/**`.
- `docs/release/**`, `repo/**`, `release/**`, `updates/**`, `security/**`.
- Existing `.aide/memory/**`, `.aide/queue/**`, `.aide/context/dominium-doctrine-refs.md`, `.aide/evals/**`, and target-generated AIDE reports.

## Preservation Risks

- Existing target AIDE memory contains stale source/local path references from the original Q23 import and should be refreshed carefully, not overwritten.
- The repo has many generated/audit/build outputs and ignored local roots; Q50 must distinguish target state from install candidates.
- Dominium doctrine has protected ownership splits (`schema`/`schemas`, `specs/reality`/`data/reality`, `packs`/`data/packs`) that Q50 must preserve.
