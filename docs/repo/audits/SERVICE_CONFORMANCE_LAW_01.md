Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Task: SERVICE-CONFORMANCE-LAW-01
Worker: 1
Stability: provisional
Result: PASS

# SERVICE-CONFORMANCE-LAW-01 Audit

## Scope

Defined a narrow service conformance substrate for future product, app,
Workbench, runtime, and tool-facing service declarations.

This is doctrine, contract, fixture, and validator work only. It does not
authorize runtime implementation, provider calls, product features, Workbench UI,
lifecycle behavior, state externalization, replay, snapshot, or live-ops work.

## Invariants Upheld

- `docs/canon/constitution_v1.md`: A1 determinism, A2 process-only mutation,
  A3 law-gated authority, A7 truth/perceived/render separation, A9 pack-driven
  integration, C1/C4 compatibility and no silent coercion.
- `docs/canon/glossary_v1.md`: Service declarations use Law, Authority,
  Process, Truth, Perceived, Rendered, Capability, and Refusal vocabulary in
  the canonical sense.
- `AGENTS.md`: extend over replace, authority ordering, contract/schema
  discipline, honest validation, and no runtime work during this
  doctrine/contract lane.
- `docs/runtime/RUNTIME_SERVICES.md`: services are bounded runtime-facing
  mediation or hosting structures and do not own semantics, product meaning, or
  truth.
- `docs/architecture/SERVICES_AND_PRODUCTS.md`: services affect access only;
  they do not rewrite history, invalidate replay, or alter past state.

## Contract And Schema Impact

Added a new provisional service conformance contract/schema/registry under
`contracts/service/**`.

No existing contract, schema, command, module, diagnostic, capability, provider,
runtime, release, canon, or planning artifact was changed.

## Artifacts

- `contracts/service/service_conformance.contract.toml`
- `contracts/service/service_conformance.schema.json`
- `contracts/service/service_class.registry.json`
- `tools/validators/contracts/check_service_conformance.py`
- `tests/contract/service_conformance/README.md`
- `tests/contract/service_conformance/fixtures/*.json`
- `tests/contract/service_conformance/service_conformance_validator_tests.py`
- `docs/architecture/service_conformance_law.md`
- `docs/repo/audits/SERVICE_CONFORMANCE_LAW_01.md`

## Validation

Run on 2026-05-21:

- `py -3 .aide/scripts/aide_lite.py doctor` — PASS.
- `py -3 .aide/scripts/aide_lite.py validate` — PASS with existing warnings
  about missing review packet refs.
- `python tools/validators/contracts/check_service_conformance.py --repo-root . --strict --fixtures` — PASS; 8 service classes, 5 fixtures, 1 valid, 4 invalid.
- `python tests/contract/service_conformance/service_conformance_validator_tests.py` — PASS; 2 tests.
- `python -m py_compile tools/validators/contracts/check_service_conformance.py tests/contract/service_conformance/service_conformance_validator_tests.py` — PASS.
- JSON parse check for `contracts/service/*.json` and service conformance
  fixtures — PASS; 7 JSON artifacts.
- `python tools/validators/contracts/check_service_conformance.py --repo-root . --list-classes` — PASS; deterministic sorted class list.
- `git diff --check` — PASS.
- Created-file whitespace check over this task's 13 written files — PASS.

Not run:

- `py -3 .aide/scripts/aide_lite.py pack --task ...` was intentionally skipped
  because it writes `.aide/context/latest-*`, which this task forbids.
- Broad runtime, provider, product, Workbench, CTest, release, and full-gate
  validation were not run because this task is a narrow contract/validator lane
  and broad feature work remains blocked.
