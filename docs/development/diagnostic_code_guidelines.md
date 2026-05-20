Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `contracts/diagnostics/diagnostic_policy.contract.toml`, `contracts/diagnostics/diagnostic_code.schema.json`

# Diagnostic Code Guidelines

Use diagnostic codes for conditions that need to be stable, searchable,
recoverable, or portable across command results, validation reports, Workbench,
release proof, support bundles, AIDE/Codex evidence, and tests.

## Naming

Each diagnostic should have:

- a dotted stable ID, such as `dominium.diagnostic.command.invalid_input`;
- a display code, such as `DOM-CMD-INVALID-INPUT`;
- an owner, such as `contracts.command` or `tools.repo`.

Use `DOM-` display codes for Dominium-owned diagnostics. Keep words uppercase and
hyphen separated. Do not encode file paths or temporary implementation details in
diagnostic IDs.

## Required Fields

Every active diagnostic entry must include:

- `id`
- `code`
- `owner`
- `severity`
- `category`
- `stability`
- `summary`
- `cause`
- `recovery`
- `evidence_expectation`

Use `related_refusal_codes`, `related_command_ids`, `related_public_surface_ids`,
and `related_artifact_types` when the relationship is known.

## Severity

Choose the lowest honest severity:

- `trace` and `debug` are diagnostic detail, not user-facing failure.
- `info` and `notice` are noteworthy but not failures.
- `warning` means the operation can continue, but the condition is actionable or
  affects trust.
- `error` means the requested action failed or must be corrected.
- `fatal` means the current process, session, or release path cannot continue.

Do not call a warning harmless unless the registry explains why it does not
affect the current gate.

## Category

Categories route diagnostics to owners. Use the registry in
`contracts/diagnostics/diagnostic_category.registry.json`. If no category fits,
use `unknown` only as a short-term provisional classification and add a follow-up
to replace it.

## Recovery Text

Recovery text should be actionable. Prefer:

```text
Run the public surface validator and update the registry entry or schema path.
```

Avoid:

```text
Something went wrong.
```

## Evidence

Every diagnostic should say what evidence proves it. Examples include a validator
JSON report, command result document, CTest output, support bundle, AIDE status
report, or release proof packet.

Evidence packets are proof output. They do not become source truth unless a
contract promotes a fixture, corpus, or registry entry.

## Refusals And Commands

Use a refusal code when the system intentionally declines an operation. Use a
diagnostic code to describe the condition behind the refusal.

Commands that return `refused`, `warning`, or `error` should cite diagnostic
codes as the command/result surface matures. UI surfaces should display the code,
summary, recovery, and evidence reference instead of inventing separate meanings.

## Stability

Most new diagnostics should start `provisional`. Promote to `stable` only after
the owning registry, command/result contract, compatibility policy, proof, and
replacement process are in place.
