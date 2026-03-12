Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Derived from `docs/contracts/CAPABILITY_NEGOTIATION_CONSTITUTION.md`, `docs/compat/ENDPOINT_DESCRIPTORS.md`, `src/compat/capability_negotiation.py`, `src/client/local_server/local_server_controller.py`, `src/server/server_console.py`, and `src/embodiment/tools/logic_tool.py`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CAP-NEG-3 Retro Audit

## Scope
- Existing CAP-NEG descriptor defaults and negotiation records
- Existing optional-capability degrade-plan generation
- Existing loopback/local-singleplayer runtime surfaces
- Existing product capability defaults

## Findings
- CAP-NEG-0 through CAP-NEG-2 already emit deterministic `degrade_plan` rows in `NegotiationRecord`.
- Degrade rules currently live inline in product defaults and product registry rows instead of a dedicated ladder registry.
- Runtime enforcement is incomplete:
  - rendered-to-TUI fallback is not exposed as a shared runtime compat state
  - logic-debug tooling does not yet refuse from negotiated feature disables
  - server console does not expose negotiated degrade state as an operator command
- Silent disable risk remains because products do not yet share a single fallback-map source of truth.
- Unknown capabilities are already ignored deterministically after capability-registry filtering; CAP-NEG-3 must preserve that behavior.

## Required CAP-NEG-3 Additions
- Canonical degrade-ladder doctrine
- Dedicated degrade ladder and fallback-map schemas/registries
- NegotiationRecord expansion for substituted capabilities
- Runtime degrade enforcement and explain surfaces
- Product/operator-visible compat status output
- RepoX/AuditX/TestX coverage for silent-disable prevention
