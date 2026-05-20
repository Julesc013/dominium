# Dependency Direction Contract Fixtures

These fixtures document the first dependency-direction validator expectations.
They are intentionally small JSON edge sets, not product code.

- `valid_dependency_edges.json` contains broad edges the law permits.
- `invalid_engine_to_runtime.json` models the forbidden `engine -> runtime` edge.
- `invalid_contracts_to_runtime.json` models the forbidden `contracts -> runtime` edge.
- `invalid_runtime_to_apps.json` models the forbidden `runtime -> apps` edge.

The active validator is:

```powershell
python tools/validators/repo/check_dependency_directions.py --repo-root . --strict
```
