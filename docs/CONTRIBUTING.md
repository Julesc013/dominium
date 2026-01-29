# Contributing Guide (CLEAN1)

Status: binding for contributor workflow.

This is the canonical contribution guide. Root-level `CONTRIBUTING.md` should
link here if present.

## DRP-1 (Data-First Policy)

- Prefer data and schemas over new code.
- Express new behavior via packs, processes, and constraints when possible.
- Code changes are allowed only when a prompt explicitly authorizes them.

## LOCKLIST and invariants

- The locklist is authoritative: `docs/architecture/LOCKLIST.md`.
- Frozen items require explicit overrides with expiry in `docs/architecture/LOCKLIST_OVERRIDES.json`.
- Overrides are forbidden on release/stable branches and must be visible in CI output.
- Invariant tests under `tests/invariant/` are fatal and run on every PR.
- LOCKLIST categories are binding:
- FROZEN: changes require an override and an expiry.
- RESERVED: do not implement yet; space is intentionally held.
- EVOLVING: changeable within DRP-1 and contract rules.

## TestX and RepoX enforcement

- TestX suites are the contract enforcement layer and are non‑negotiable.
- RepoX policies prevent forbidden symbols, paths, and structural violations.
- If tests or RepoX fail, fix the change. Do not mute the guardrails.

## When code changes are allowed

- Only when a prompt explicitly permits code changes in its scope.
- Never for data-only prompts or documentation-only prompts.
- Any code change must preserve determinism, refusal semantics, and authority.
- If engine/ or game/ changes are made, add an entry to `CODE_CHANGE_JUSTIFICATION.md` that answers:
  "Why can this not be data?"

## Adding data safely

- Use namespaced identifiers and never reuse IDs.
- Follow `docs/architecture/ID_AND_NAMESPACE_RULES.md`.
- Include unit annotations and fixed-point guidance where applicable.
- Preserve unknown fields on read/write paths.

## Proposing new primitives

- Provide a data-first attempt and document the gap.
- Create a design note and link it from `docs/architecture/CHANGELOG_ARCH.md`.
- Expect review against `docs/architecture/CODE_KNOWLEDGE_BOUNDARY.md`.

## What will be rejected and why

- Code changes that can be expressed as data.
- New mechanics in data‑only or documentation‑only prompts.
- Silent fallbacks that hide incompatibility or missing capabilities.
- Identifier reuse or schema changes without versioning.
- Any change that weakens determinism, refusal semantics, or authority rules.

## Review expectations

- Determinism and refusal behavior must be explicit.
- Frozen contracts require explicit change logs and hash updates.
- Tests should include deterministic fixtures and refusal coverage.
- Invariant or RepoX failures are release-blocking by default.

## Canonical contracts

All normative contracts live under `docs/architecture/`.
Start with `docs/architecture/CONTRACTS_INDEX.md`.
