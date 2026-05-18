# MOVE-FAMILY-00B-GATE Blockers

## Blocking Issues

None.

## Non-Blocking Warnings

- `contracts/projection/ide/**` is absent today and must be created only by the later approved apply task.
- Historical/audit references to old `ide/manifests/**` paths are intentionally not rewritten.
- Generated-output references to `ide/manifests/*.projection.json` remain review/later items because they do not point at the tracked schema/example source files.
- Strict validators emit known TOML fallback-parser warnings while returning strict pass.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration were out of scope.

## Deferred Risks

- The apply task must update the five apply rewrite groups exactly and then scan for stale `ide/manifests` tracked-source references.
- The apply task must prove `git ls-files ide` is empty before retiring the `ide` layout exception.
- The apply task must keep generated IDE projection outputs ignored and uncommitted.

## Apply Authorization Status

MOVE-FAMILY-00B-APPLY is authorized with warnings.

Authorized scope:

```text
ide/manifests/projection_manifest.schema.json -> contracts/projection/ide/projection_manifest.schema.json
ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json -> contracts/projection/ide/examples/example_linux_clang_modern_client_gui.projection.json
ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json -> contracts/projection/ide/examples/example_win_vc6_win9x_client_gui.projection.json
```

All other moves remain unauthorized.
