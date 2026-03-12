Status: CANONICAL
Last Reviewed: 2026-03-03
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Institutional Communication Baseline (SIG-6)

## Scope
SIG-6 establishes deterministic institutional communication and aggregation over existing SIG-0..5 transport/message/trust layers. Implemented outputs are REPORT/MODEL/CREDENTIAL artifacts routed through signal transport, with no direct schedule mutation and no epistemic bypass.

## Bulletin Model
- Engine: `src/signals/institutions/bulletin_engine.py`
- Input surfaces:
  - MAT events
  - MOB travel events + congestion occupancy
  - MOB/MAT wear state
  - SPEC compliance rows
- Output:
  - deterministic REPORT artifacts (`artifact.report.institution.*`)
  - dispatch via `process_signal_send`
- Budget behavior:
  - deterministic ordering by institution id
  - deterministic degrade to coarse summary + deferred institutions

## Dispatch Integration
- Engine: `src/signals/institutions/dispatch_engine.py`
- Policy source: `data/registries/dispatch_policy_registry.json`
- Behavior:
  - accepts policy-compliant dispatch updates
  - emits `ControlIntent` rows via `build_control_intent`
  - routes schedule changes through `process.travel_schedule_set` inputs
  - emits dispatch REPORT artifacts and signal envelopes
- Refusal:
  - `refusal.dispatch.policy_forbidden`

## Standards and Certification Workflow
- Engine: `src/signals/institutions/standards_engine.py`
- Policy source: `data/registries/standards_policy_registry.json`
- Behavior:
  - deterministic spec issue request handling
  - deterministic CREDENTIAL artifact issuance
  - deterministic MODEL artifact linkage to credentials/specs
  - compliance REPORT publication through SIG transport
- Refusal:
  - `refusal.standards.spec_type_forbidden`

## UX and Inspection Summary
- Inspection sections integrated:
  - `section.institution.bulletins`
  - `section.institution.dispatch_state`
  - `section.institution.compliance_reports`
- Supports diegetic board/panel/terminal presentation through existing inspection + signal receipt pathways.

## Trust and Acceptance
- Institutional sender identities are normalized to `subject.institution.*` when explicit sender is not supplied.
- Receipt acceptance remains policy/trust-gated in SIG-5 (`accepted` vs `untrusted`), preserving epistemic separation.

## Schemas and Registries
- Schemas:
  - `schema/signals/institution_profile.schema`
  - `schema/signals/bulletin_policy.schema`
  - `schema/signals/dispatch_policy.schema`
  - `schema/signals/standards_policy.schema`
- Registries:
  - `data/registries/bulletin_policy_registry.json`
  - `data/registries/dispatch_policy_registry.json`
  - `data/registries/standards_policy_registry.json`
- CompatX version entries added in `tools/xstack/compatx/version_registry.json`.

## Validation Evidence
- RepoX FAST: PASS (`python tools/xstack/repox/check.py --profile FAST`)
- RepoX STRICT: PASS (`python tools/xstack/repox/check.py --profile STRICT`)
- AuditX run:
  - FAST run completed (`python tools/xstack/auditx/check.py --profile FAST`)
  - STRICT run completed (`python tools/xstack/auditx/check.py --profile STRICT`)
- TestX (SIG-6 required cases): PASS
  - `testx.signals.institutions.bulletin_generation_deterministic`
  - `testx.signals.institutions.dispatch_updates_go_through_ctrl`
  - `testx.signals.institutions.standards_issues_spec_and_credential`
  - `testx.signals.institutions.report_acceptance_depends_on_trust`
  - `testx.signals.institutions.budget_degrade_reports`
- Topology map refreshed:
  - `python tools/governance/tool_topology_generate.py --repo-root .`

### Strict Gate Note
`python scripts/dev/gate.py strict --repo-root . --profile-report` currently returns non-zero because `testx.group.core.invariants` reports `required_tests_missing` in this workspace baseline. This is pre-existing gate behavior unrelated to SIG-6 institutional logic changes.

## Extension Points
- ECO:
  - bulletin/report channels can carry deterministic market/public service summaries.
- MIL:
  - institutional campaign/dispute messaging can layer on trust/verification without bypassing SIG transport.
- SCI:
  - standards/certification publications can extend REPORT/MODEL/CREDENTIAL outputs with domain-specific schemas.
