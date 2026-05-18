Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Semantic Lint Disposition

Semantic lint gates exist to prevent accidental hardcoded identity, world, profile, schema, and physical-assumption literals from bypassing contracts, registries, manifests, profiles, and deterministic configuration.

They do not forbid every literal. They require every flagged literal to be fixed or explicitly classified.

## Disposition Classes

Allowed preserve classes:

- `preserve_doctrine_constant`: intentional doctrine-backed vocabulary or constants documented by canon, MVP scope, worldgen doctrine, pack doctrine, or audit doctrine.
- `preserve_fixture_literal`: fixture, expected-output, or TestX literal used to verify a governed behavior.
- `preserve_protocol_literal`: protocol, pack, route, command, object, field, or release identifier that must remain stable by contract.
- `preserve_schema_literal`: schema-facing field, section, property, enum, or class vocabulary.

Fix classes:

- `fix_stale_path`: stale layout/path literal should be rewritten to current layout authority.
- `fix_stale_identifier`: stale semantic identifier should be rewritten to the current contract or registry value.
- `replace_with_contract_reference`: code should consume an existing contract surface rather than embed the value.
- `replace_with_registry_reference`: code should consume an existing registry surface rather than embed the value.

Blocker classes:

- `needs_followup`: the finding is understood but cannot be safely fixed in the current task.
- `unknown_blocker`: the finding lacks enough evidence for safe disposition.

## Allowlist Rules

Allowlist entries must be exact and reviewed. The current semantic lint allowlist is `contracts/repo/semantic_lint_allowlist.json`.

Each entry must include:

- test name
- file
- line
- validator message
- source-line SHA-256 hash
- disposition
- severity
- owner
- reason
- scope

Broad suppressions are forbidden. Do not add wildcard path, directory-wide, docs-wide, or message-class suppressions to get a green test.

## Adding Future Exceptions

For a future finding:

1. Prefer fixing stale or accidental literals.
2. Prefer a contract or registry reference when one already exists.
3. Preserve historical/audit evidence without rewriting it unless it claims current truth.
4. Add a new exact allowlist entry only when the literal is doctrine-backed, fixture-owned, protocol-owned, schema-owned, or conventional.
5. Rerun the focused semantic lint test and record the evidence.
