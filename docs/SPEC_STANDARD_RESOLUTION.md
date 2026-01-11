# SPEC_STANDARD_RESOLUTION — Standard Resolution Order and Conflict Handling

Status: draft
Version: 1

## Purpose
Define the universal, deterministic resolution order for standards and how conflicts
and UNKNOWN are handled. This order applies to time, currency, units, law, markets,
governance, and any future standards.

## Resolution order (mandatory)
1) Explicit context (contract, document, UI override)
2) Organization standard
3) Jurisdiction standard
4) Personal preference
5) Fallback canonical numeric form

Silent fallback is FORBIDDEN. Every resolution step must be explicit and auditable.

## Resolution context
The resolver receives a context containing:
- actor identity and knowledge set
- explicit documents or contracts in scope
- organization memberships and policies
- jurisdiction(s) in scope
- personal preferences
- device/access constraints (see `docs/SPEC_EPISTEMIC_GATING.md`)

## Deterministic resolution
Resolution must be deterministic given the context:
- the same context yields the same standard choice
- no wall-clock time or random inputs
- any tie-breakers are explicit and stable (e.g., canonical id ordering)

## Conflict handling
Conflicts are expected and must be visible:
- If multiple standards are valid at the same precedence level, resolve by explicit
  tie-break rules and surface a conflict flag.
- If a higher-precedence standard is blocked by epistemic gating, it becomes UNKNOWN
  and resolution proceeds to the next step with a conflict record.
- If no standard is available or permitted, render as UNKNOWN or canonical numeric form.

## UNKNOWN semantics
UNKNOWN is a first-class representation:
- UNKNOWN does not imply zero or any default value.
- UNKNOWN propagates through formatting pipelines.
- UNKNOWN must be distinguishable from "value exists but is hidden."

## Fallback canonical numeric form
If no standard can be resolved, the renderer may present a canonical numeric form
without units or labels. This is not a standard; it is a last-resort view of the
authoritative quantity.

## ASCII diagram

  [Explicit Context]
          |
          v
  [Organization Standard]
          |
          v
  [Jurisdiction Standard]
          |
          v
  [Personal Preference]
          |
          v
  [Canonical Numeric Form]

Each step can yield:
- RESOLVED (with optional conflict flag)
- BLOCKED (epistemic gating -> UNKNOWN)
- NOT_AVAILABLE (proceed)

## Non-examples (forbidden)
- "Default to the player's last used standard" without explicit context
- "Pick the first standard found in a list" without deterministic ordering
- "Assume jurisdiction from locale settings" (not authoritative, not deterministic)
- "Hide conflicts to keep UI simple"
- "Use engine defaults for standard names"

## Worked examples

### Time resolution conflict
Contract: HPC-E calendar
Organization: SCT calendar
Jurisdiction: Gregorian-like calendar
Preference: SCT

Resolution: use contract (HPC-E), flag conflict against org/jurisdiction.
If actor lacks knowledge of HPC-E, result is UNKNOWN with conflict record and
resolution proceeds to organization standard.

### Currency resolution conflict
Explicit invoice: local currency
Organization: internal currency
Jurisdiction: tax currency
Preference: local currency

Resolution: explicit invoice currency. A conflict flag is shown if the organization
or jurisdiction requires a different standard for reporting.

### Units with device failure
Explicit context: SI-like units
Device required for SI-like units is offline

Resolution: SI-like standard is blocked -> UNKNOWN, then canonical numeric form
displayed with an explicit "unknown unit" marker.

## Validation requirements (spec-only)
Implementations must provide:
- deterministic resolution tests
- conflict visibility tests
- UNKNOWN propagation tests
- refusal on silent fallback or hidden conflict
