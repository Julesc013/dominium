Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Module Development Guidelines

Use a module descriptor when a functional extension needs stable identity across
Workbench, apps, packs, providers, commands, documents, views, or evidence.

## Rules

- Choose a lowercase dotted `module_id` under `domino.*` or `dominium.*`.
- Do not use a path, filename, or generic ID such as `module.validation`.
- Pick a kind from `contracts/module/module_kind.registry.json`.
- Declare commands, services, capabilities, providers, documents, views,
  diagnostics, refusals, artifacts, tests, and proof by stable IDs.
- Mark unimplemented modules with `implementation_status = "planned"` or the
  JSON equivalent.
- Keep `implementation_path_is_identity` false.
- Stable modules require proof and replacement policy.

## Do Not

- Call private validators or tools from Workbench modules when command surfaces
  exist.
- Treat a source folder as a module without a descriptor.
- Use a module descriptor as a junk drawer for unrelated behavior.
- Activate pack-provided modules silently.

Run:

```text
python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict
python tools/validators/contracts/check_module_descriptors.py --repo-root . --fixtures
```
