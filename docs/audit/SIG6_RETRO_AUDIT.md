Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Scope: SIG-6 institutional communication and aggregation
Date: 2026-03-03
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# SIG6 Retro Audit

## Audit Scope
- `src/signals/aggregation/aggregation_engine.py`
- `src/signals/transport/transport_engine.py`
- `src/mobility/travel/travel_engine.py`
- `src/inspection/inspection_engine.py`
- `tools/xstack/sessionx/process_runtime.py`
- `data/registries/aggregation_policy_registry.json`
- `data/registries/inspection_section_registry.json`

## Findings

### F1 - Aggregation exists, but no institution policy profile binds bulletin behavior
- Current aggregation can create report artifacts deterministically, but there is no institution-scoped policy contract for bulletin cadence, audience scope, and severity routing.
- Impact: institutional bulletin behavior is possible but not canonically configured.

### F2 - Dispatch-related schedule flows exist without a dedicated institutional dispatch model
- Mobility schedules/timetables exist (`process.travel_schedule_set`, travel commitments), but no dedicated institutional dispatch engine or dispatch policy abstraction exists.
- Impact: dispatch offices cannot be represented consistently across institutions.

### F3 - Standards/certification outputs are fragmented across spec/trust systems
- Spec compliance and credential/trust primitives exist, but no institutional standards-body workflow binds spec issuance, credential issuance, and compliance report publication under one deterministic policy surface.
- Impact: standards governance lacks a single deterministic orchestration path.

### F4 - Inspection supports signal summaries but no institution report sections
- Existing inspection sections include signal/trust/mobility summaries.
- Institution bulletin/dispatch/compliance sections are not present.
- Impact: institutional comm state is not inspectable in a canonical way.

### F5 - No explicit ad-hoc schedule bypass found in audited signal modules
- Signal aggregation/transport modules do not mutate mobility schedules directly.
- Remaining risk sits in future feature additions unless explicit control-plane-only dispatch invariant checks are added.

## Ad-Hoc / Bypass Scan
- No direct schedule mutation found in signal aggregation/transport modules.
- No direct knowledge mutation bypass found in current signal transport paths (receipt process remains authoritative).
- No dedicated institutional message flow implementation exists yet, so no institutional bypass detected.

## Migration Plan
1. Add institutional profile/policy schemas and registries (`institution_profile`, `bulletin_policy`, `dispatch_policy`, `standards_policy`).
2. Implement deterministic institutional engines:
   - bulletin generation and SIG dispatch
   - dispatch-office control-intent emission for schedule updates
   - standards/certification report workflow
3. Integrate trust-weighted acceptance for institutional bulletins through existing SIG-5 receipt path.
4. Add inspection sections for bulletins, dispatch state, and compliance reports.
5. Add enforcement scaffolding:
   - `INV-INSTITUTIONAL-SCHEDULES-THROUGH-CTRL`
   - `INV-REPORTS-ARE-ARTIFACTS`
   - `INV-NO-ADHOC-BULLETINS`
6. Add AuditX analyzers for:
   - direct schedule mutation bypass
   - institutional process bypass
7. Add deterministic TestX coverage for bulletin generation, dispatch-through-control, standards issuance, trust-gated acceptance, and budget degrade behavior.
