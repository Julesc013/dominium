Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: fixture

# Project Graph Service Contract Fixtures

These fixtures prove `tools/validators/contracts/check_project_graph_service.py`
and `runtime/project_graph/service.py`.

Valid fixtures demonstrate deterministic node, edge, dependency, and proof
ordering. Invalid fixtures prove duplicate node refusal, missing dependency
target refusal, cycle refusal, and pass-proof evidence requirements.

The fixtures are contract tests only. They do not create a project UI, mutate
project truth, publish a release projection, or authorize broad feature work.
