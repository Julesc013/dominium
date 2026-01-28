# Contributing Guide (CLEAN1)

Status: binding for contributor workflow.

This is the canonical contribution guide. Root-level `CONTRIBUTING.md` should
link here if present.

## DRP-1 (Data-First Policy)

- Prefer data and schemas over new code.
- Express new behavior via packs, processes, and constraints when possible.
- Code changes are allowed only when a prompt explicitly authorizes them.

## When code changes are allowed

- Only when a prompt explicitly permits code changes in its scope.
- Never for data-only prompts or documentation-only prompts.
- Any code change must preserve determinism, refusal semantics, and authority.

## Adding data safely

- Use namespaced identifiers and never reuse IDs.
- Follow `docs/architecture/ID_AND_NAMESPACE_RULES.md`.
- Include unit annotations and fixed-point guidance where applicable.
- Preserve unknown fields on read/write paths.

## Proposing new primitives

- Provide a data-first attempt and document the gap.
- Create a design note and link it from `docs/architecture/CHANGELOG_ARCH.md`.
- Expect review against `docs/architecture/CODE_KNOWLEDGE_BOUNDARY.md`.

## Review expectations

- Determinism and refusal behavior must be explicit.
- Frozen contracts require explicit change logs and hash updates.
- Tests should include deterministic fixtures and refusal coverage.

## Canonical contracts

All normative contracts live under `docs/architecture/`.
Start with `docs/architecture/CONTRACTS_INDEX.md`.
