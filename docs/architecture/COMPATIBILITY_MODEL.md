# Compatibility Model (OPS1)

Status: FROZEN.  
Scope: compatibility reporting, mode selection, and mixed-version rules.

## Compat Report (Mandatory)
Every load, join, run, update, or migrate operation MUST emit a compat_report.
No operation may proceed without one. compat_report is both human- and
machine-readable and is included in bugreport bundles.

Schema:
- `schema/compat.report.schema`

Required contexts:
- `load`
- `join`
- `run`
- `update`
- `migrate`

## Compatibility Modes (Locked)

| Mode | Meaning | Allowed actions |
| --- | --- | --- |
| `full` | All required capabilities present | Normal execution |
| `degraded` | Non-critical capabilities missing | Execution allowed with explicit feature loss |
| `frozen` | Authoritative simulation halted | Inspect, replay, export only |
| `inspect-only` | Read-only access | Inspection and diagnostics only |
| `refuse` | Operation blocked | No execution; explicit refusal |

Rules:
- Mode selection MUST be logged and surfaced.
- Modes MUST NOT be chosen silently.
- Mixed semantics within a single authoritative domain are forbidden.

## Mixed Version Rules

Client ↔ Server:
- Client may connect only if capability baseline overlap is non-empty.
- Missing server capabilities ⇒ `refuse`.
- Missing client capabilities ⇒ `degraded` or `inspect-only`.

Server ↔ Server (Shards):
- Shards may run different binaries.
- Domain ownership transfer requires sufficient capability overlap.
- Cross-shard messages include capability context in compat_report metadata.

Tools ↔ Everything:
- Tools may inspect newer/older artifacts.
- Tools MUST NOT mutate state when compatibility is degraded.

## Migration Semantics (Honest)

Transform-only migration:
- Original save/replay remains valid.
- A new artifact is created with a new version.
- No in-place destructive migration is allowed.

Refusal of impossible migration:
- If semantics cannot be preserved, the operation MUST refuse.
- compat_report must explain why and include refusal codes.

## Reporting Requirements

compat_report MUST include:
- capability_baseline
- required_capabilities, provided_capabilities, missing_capabilities
- compatibility_mode
- refusal_codes and mitigation_hints (if applicable)
```
