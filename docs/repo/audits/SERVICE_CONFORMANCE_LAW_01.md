Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: prior narrow service-class audit
Superseded By: none
Task: SERVICE-CONFORMANCE-LAW-01
Stability: provisional
Result: PASS_WITH_WARNINGS

# SERVICE-CONFORMANCE-LAW-01 Audit

## Scope

Created the service/provider conformance law for replaceable runtime services and providers. The work is limited to contracts, schemas, registries, fixtures, documentation, and validation.

## Invariants Upheld

- Canon A1/A2/A3/A7/A9: deterministic proof, process-only mutation, law-gated authority, truth/perceived/render separation, and explicit pack/capability behavior.
- `AGENTS.md`: extend over replace, contract discipline, honest validation, and no runtime implementation in a contract lane.
- Provider, capability/refusal, command, diagnostics, artifact, replacement, versioning, public-surface, app, module, and Workbench laws are referenced rather than replaced.

## Changed

- Added service descriptor law and registry surfaces under `contracts/service/**`.
- Added service/provider conformance suite law and registries under `contracts/conformance/**`.
- Cross-linked provider descriptors to implemented services and conformance suites.
- Added service/provider diagnostics, refusals, capability, artifact kinds, and public-surface entries needed for validation.
- Added positive and negative fixtures under `tests/contract/service/**` and `tests/contract/conformance/**`.
- Replaced `tools/validators/contracts/check_service_conformance.py` with a validator for service descriptors, conformance suites, provider service refs, fixtures, JSON output, strict mode, and inventory mode.

## Non-Goals

No runtime service dispatch, provider resolver, provider runtime loading, renderer/platform/storage/network/audio/input/package/profile services, Workbench UI, module runtime, gameplay/domain code, CMake targets, or full CTest run were added.

## Result

PASS_WITH_WARNINGS is expected because current service/provider entries are planned or fixture-only and intentionally carry no runtime support claim.

## Follow-Up

Next recommended task: `DOCUMENT-PATCH-TRANSACTION-RUNTIME-01`.
