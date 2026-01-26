# Refusal Semantics (REFUSE0)

Status: binding.
Scope: unified refusal taxonomy and payload contracts.

## Purpose
Refusals are first-class, deterministic outcomes. They must be identical across
CLI/TUI/GUI/tools, with stable codes and structured payloads.

## Refusal payload (minimum shape)
```
refusal:
  code_id: <small integer>
  code: <stable token>
  message: <short summary>
  details: <map>
  explanation_classification: PUBLIC | PRIVATE | ADMIN
```

## Canonical refusal codes (stable, small integers)
```refusal-codes
# code_id, code, meaning
1, REFUSE_INVALID_INTENT, Invalid or malformed intent or parameters
2, REFUSE_LAW_FORBIDDEN, Law evaluation forbids the action
3, REFUSE_CAPABILITY_MISSING, Required capability is missing
4, REFUSE_DOMAIN_FORBIDDEN, Domain or jurisdiction forbids the action
5, REFUSE_INTEGRITY_VIOLATION, Integrity signals block the action
6, REFUSE_RATE_LIMIT, Rate limit exceeded
7, REFUSE_BUDGET_EXCEEDED, Budget policy refusal
1001, WD-REFUSAL-INVALID, Invalid or incomplete WorldDefinition
1002, WD-REFUSAL-SCHEMA, Unsupported WorldDefinition schema version
1003, WD-REFUSAL-CAPABILITY, Missing capability for WorldDefinition
1004, WD-REFUSAL-TEMPLATE, Template refusal (invalid parameters or guarantees)
```

Rules:
- code_id and code are immutable once released.
- All surfaces must emit the same code_id/code for the same condition.
- New refusals require new code_id (no reuse).

## Structured payloads
- details MUST be a map.
- Do not embed raw file paths in details.
- details should include stable ids (capability_id, policy_id, schema_id).

## Cross-surface consistency
- CLI/TUI/GUI/tools MUST surface identical refusal codes and payload shape.
- Presentation may change, semantics may not.

## See also
- `docs/arch/REFUSAL_AND_EXPLANATION_MODEL.md`
- `schema/integrity/SPEC_REFUSAL_CODES.md`
