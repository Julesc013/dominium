# Refusal Semantics (REFUSE0)

Status: binding.
Scope: unified refusal taxonomy and payload contracts.

## Purpose
Refusals are first-class, deterministic outcomes. They must be identical across
CLI/TUI/GUI/tools and across SP/MP/MMO, with stable codes and structured
payloads.

## Invariants
- Refusals are authoritative outcomes with no state mutation.
- Refusal meaning is stable across all products and modes.
- Refusals are surfaced everywhere the action can be observed.
- Codes are small integers with stable symbolic names.

## Refusal payload (minimum shape)
```
refusal:
  code_id: <small integer>
  code: <stable token>
  message: <short summary>
  details: <map>
  explanation_classification: PUBLIC | PRIVATE | ADMIN
```

Payload rules:
- `code_id` is the canonical small integer code.
- `code` is the canonical symbolic token.
- `details` MUST be a map with stable identifiers where possible.
- `details` MUST NOT contain raw absolute file paths.

## Canonical refusal code table (binding)
| code_id | code | meaning |
| --- | --- | --- |
| 1 | REFUSE_INVALID_INTENT | Invalid or malformed intent or parameters |
| 2 | REFUSE_LAW_FORBIDDEN | Law evaluation forbids the action |
| 3 | REFUSE_CAPABILITY_MISSING | Required capability is missing |
| 4 | REFUSE_DOMAIN_FORBIDDEN | Domain or jurisdiction forbids the action |
| 5 | REFUSE_INTEGRITY_VIOLATION | Integrity signals block the action |
| 6 | REFUSE_RATE_LIMIT | Rate limit exceeded |
| 7 | REFUSE_BUDGET_EXCEEDED | Budget policy refusal |
| 701 | REFUSE_ACTIVE_DOMAIN_LIMIT | Tier-2 active domain budget exceeded |
| 702 | REFUSE_REFINEMENT_BUDGET | Refinement budget exceeded |
| 703 | REFUSE_MACRO_EVENT_BUDGET | Macro event budget exceeded |
| 704 | REFUSE_AGENT_PLANNING_BUDGET | Agent planning budget exceeded |
| 705 | REFUSE_SNAPSHOT_BUDGET | Snapshot or serialization budget exceeded |
| 706 | REFUSE_COLLAPSE_BUDGET | Collapse or compaction budget exceeded |
| 707 | REFUSE_DEFER_QUEUE_LIMIT | Deferred work queue limit exceeded or disabled |
| 1001 | WD-REFUSAL-INVALID | Invalid or incomplete WorldDefinition |
| 1002 | WD-REFUSAL-SCHEMA | Unsupported WorldDefinition schema version |
| 1003 | WD-REFUSAL-CAPABILITY | Missing capability for WorldDefinition |
| 1004 | WD-REFUSAL-TEMPLATE | Template refusal (invalid parameters or guarantees) |

## Machine-readable canonical refusal codes (do not reorder lightly)
```refusal-codes
# code_id, code, meaning
1, REFUSE_INVALID_INTENT, Invalid or malformed intent or parameters
2, REFUSE_LAW_FORBIDDEN, Law evaluation forbids the action
3, REFUSE_CAPABILITY_MISSING, Required capability is missing
4, REFUSE_DOMAIN_FORBIDDEN, Domain or jurisdiction forbids the action
5, REFUSE_INTEGRITY_VIOLATION, Integrity signals block the action
6, REFUSE_RATE_LIMIT, Rate limit exceeded
7, REFUSE_BUDGET_EXCEEDED, Budget policy refusal
701, REFUSE_ACTIVE_DOMAIN_LIMIT, Tier-2 active domain budget exceeded
702, REFUSE_REFINEMENT_BUDGET, Refinement budget exceeded
703, REFUSE_MACRO_EVENT_BUDGET, Macro event budget exceeded
704, REFUSE_AGENT_PLANNING_BUDGET, Agent planning budget exceeded
705, REFUSE_SNAPSHOT_BUDGET, Snapshot/serialization budget exceeded
706, REFUSE_COLLAPSE_BUDGET, Collapse or compaction budget exceeded
707, REFUSE_DEFER_QUEUE_LIMIT, Deferred work queue limit exceeded or disabled
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
- SP/MP/MMO MUST use identical refusal meaning for identical conditions.
- CLI/TUI/GUI/tools/network MUST surface identical codes and payload shape.
- Presentation may change, semantics may not.

## See also
- `docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md`
- `schema/integrity/SPEC_REFUSAL_CODES.md`
