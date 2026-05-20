# Provider Model Contract Fixtures

These fixtures document expected behavior for
`tools/validators/contracts/check_provider_model.py`.

Valid fixtures cover provider descriptors and provider selection decisions.
Invalid fixtures prove that provider IDs, kinds, capability references, stable
conformance proof, and silent fallback behavior remain governed.

The fixtures are contract tests only. They do not implement provider runtime
loading, renderer fallback, platform binding, package/profile loaders, Workbench
UI, or native plugin behavior.
