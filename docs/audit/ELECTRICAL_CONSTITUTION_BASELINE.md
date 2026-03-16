Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Electrical Constitution Baseline

Status: Baseline complete (ELEC-0)
Date: 2026-03-03

## Scope Summary

ELEC-0 establishes governance, schema/registry scaffolding, and enforcement for electrical simulation without introducing a bespoke runtime solver.

Electrical behavior is constrained to existing substrates:

- topology: `NetworkGraph`
- transport: `FlowSystem` + `QuantityBundles`
- response: `ConstitutiveModels`
- protection: `SAFETY` patterns
- compliance: `SPEC` checks
- control/audit: `CTRL` process and decision logs

## Tiering Definition

- `E0` macro: global bookkeeping, coarse loss policy, deterministic everywhere.
- `E1` meso: phasor approximation (`P/Q/S`, PF) for budget-approved networks.
- `E2` micro: waveform-level optional lab/ROI tier only.

## Quantities

- Canonical electrical flow bundle: `bundle.power_phasor = {P, Q, S}`.
- `V` and `I` remain derived quantities in ELEC-0 baseline.
- Losses are represented as deterministic transforms and hooks toward thermal accounting.

## Safety Requirements

Electrical protection must route through SPL templates:

- breaker trip/disconnect
- fail-safe default off
- interlock and lockout-tagout
- redundancy/islanding and hazard hooks

No ad-hoc inline breaker/protection logic is permitted outside SAFETY process paths.

## Integration Points

THERM:

- electrical losses and overload heat are modeled as deterministic transform hooks for thermal domains.

FLUID:

- pump/compressor drive coupling is expressed via model bindings and flow bundle interfaces, not domain-specific electric hacks.

LOGIC:

- control and automation commands (switching, lockout, dispatch) remain ControlIntent/IR-driven with process-only mutation.

SIG:

- compliance/fault reporting uses INFO artifacts and signal transport (no direct omniscient propagation).

## Artifacts Added In ELEC-0

Documentation:

- `docs/audit/ELEC0_RETRO_AUDIT.md`
- `docs/electric/ELECTRICAL_CONSTITUTION.md`

Governance updates:

- `docs/meta/REAL_WORLD_AFFORDANCE_MATRIX.md`
- `data/meta/real_world_affordance_matrix.json`
- `docs/meta/ACTION_GRAMMAR_CONSTITUTION.md`
- `docs/meta/INFORMATION_GRAMMAR_CONSTITUTION.md`
- `data/registries/action_template_registry.json` (electrical action templates)
- `data/registries/control_action_registry.json` (electrical control-action stubs)

Electrical registries:

- `data/registries/elec_node_kind_registry.json`
- `data/registries/elec_edge_kind_registry.json`
- `data/registries/elec_model_registry.json`
- `data/registries/elec_spec_templates.json`

Enforcement:

- RepoX rules:
  - `INV-ELEC-USES-FLOW-BUNDLE`
  - `INV-ELEC-SAFETY-THROUGH-PATTERNS`
  - `INV-NO-ADHOC-PF-LOGIC`
- AuditX analyzers:
  - `E183_ELECTRIC_SPECIAL_CASE_SMELL`
  - `E184_BREAKER_BYPASS_SMELL`

TestX:

- `test_elec0_docs_present`
- `test_elec0_registry_presence`

## Readiness Checklist For ELEC-1

- [x] Tier model defined (`E0/E1/E2`)
- [x] Quantity contract declared (`bundle.power_phasor`)
- [x] Node/edge/model/spec IDs reserved via registries
- [x] Safety and compliance constraints documented
- [x] RWAM and grammar mappings declared
- [x] RepoX/AuditX guardrails added
- [x] Baseline tests added for docs/registry presence
- [ ] Power flow solver implementation (deferred to ELEC-1+)
- [ ] Waveform simulation (deferred to E2 lab series)

## Gate Results

Executed commands:

- RepoX STRICT:
  - `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: **REFUSAL** due pre-existing repository issue:
    - `INV-NO-RANKED-FLAGS` in `tools/signals/tool_run_sig_stress.py` (`ranked_mode` flag usage).
  - ELEC-0-specific refusals introduced during implementation were resolved (action registry and topology registration fixes applied).
- AuditX scan:
  - `python tools/auditx/auditx.py scan --repo-root . --format both`
  - Result: **COMPLETE** (`findings_count=1390`), outputs refreshed under `docs/audit/auditx/`.
- TestX (doc/registry validation):
  - `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_elec0_docs_present,test_elec0_registry_presence`
  - Result: **PASS** (`2/2`).
- Strict build gate:
  - `python scripts/dev/gate.py strict --repo-root . --only-gate build_strict`
  - Result: **PASS**.
- Topology map refresh:
  - `python tools/governance/tool_topology_generate.py --repo-root .`
  - Result: **PASS** (`fingerprint=e5a129601280608f99a39cccc068ef06a399917e9523461361cec2301f604195`).
