# Setup Guide (SHIP-1)

Status: binding.
Scope: canonical setup workflows and CLI-first usage.

Setup is offline-first and transactional. CLI is canonical; TUI/GUI wrappers
delegate to the same CLI semantics and logs.

## Install (minimal or maximal)

Minimal distribution includes binaries only. Maximal distribution may include
bundled packs. Setup does not branch logic; it treats any bundled content as
already present.

CLI example:
```
setup --deterministic 1 install --manifest <artifact_root>/setup/manifests/product.dsumanifest \
  --install-root <install_root> --data-root <data_root>
```

Outputs:
- `INSTALL_ROOT/install.manifest.json`
- `INSTALL_ROOT/compat_report.json`
- `INSTALL_ROOT/ops/ops.log`
- `INSTALL_ROOT/setup_state.json`

## Repair

```
setup --deterministic 1 repair --manifest <artifact_root>/setup/manifests/product.dsumanifest \
  --install-root <install_root>
```

Repair re-stages missing binaries and preserves user data.

## Uninstall

```
setup uninstall --install-root <install_root>
```

By default, uninstall removes the install root only and preserves data_root.
To remove data explicitly:
```
setup uninstall --install-root <install_root> --remove-data
```

## Rollback

```
setup rollback --install-root <install_root>
```

Rollback restores the most recent backup created during repair/update.

## Notes

- Use `--data-root` to relocate data to a separate path.
- Use `--network-mode offline|online|auto` for explicit network handling.
- Setup never assumes content packs exist; missing packs do not block install.

## References

- `docs/distribution/SETUP_GUARANTEES.md`
- `docs/architecture/SETUP_TRANSACTION_MODEL.md`
