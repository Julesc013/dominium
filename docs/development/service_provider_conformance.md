Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `docs/architecture/service_conformance_law.md`, `docs/architecture/provider_conformance_law.md`, `contracts/service/service.contract.toml`, `contracts/conformance/conformance.contract.toml`

# Service And Provider Conformance

## Descriptor Workflow

1. Add or update a service descriptor in `contracts/service/service.registry.json`.
2. Add provider service relationships in `contracts/provider/provider.registry.json` only when the provider declares `implemented_service_ids`.
3. Add a conformance suite in `contracts/conformance/conformance.registry.json`.
4. Add positive and negative fixtures under `tests/contract/service/fixtures` or `tests/contract/conformance/fixtures`.
5. Run `python tools/validators/contracts/check_service_conformance.py --repo-root . --strict`.

## Support Claims

`planned` and `fixture_only` are allowed descriptor states. They are not support. A service or provider cannot claim stable support until it has a matching `passing` conformance suite and the replacement/versioning policies are satisfied.

## Validator Modes

- `--strict` validates contracts, registries, descriptors, cross-references, and fixtures.
- `--json` emits deterministic machine-readable output.
- `--fixtures` validates fixture expectations without requiring runtime.
- `--inventory` reports service/provider-like surfaces as descriptive warning output only.

## Boundaries

The validator is repo tooling. Runtime code must not depend on it. Runtime support must be added by later scoped tasks that implement services, provider resolution, backend loading, Workbench runtime, or product behavior with their own evidence.
