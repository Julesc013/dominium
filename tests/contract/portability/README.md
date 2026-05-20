Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: fixture

# Portability Contract Fixtures

These fixtures prove `tools/validators/platform/check_portability_matrix.py`.

Valid fixtures demonstrate platform floor, toolchain, evidence, and runtime row shapes. Invalid fixtures prove that supported/stable claims require evidence, unknown toolchains are rejected, and product modes must reference runtime capabilities.

The fixtures are contract tests only. They do not create platform support, install toolchains, add build targets, or publish release artifacts.
