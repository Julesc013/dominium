# Linux Packaging (tar.gz + deb + rpm)

## Outputs

- `dist/linux/dominium-x.y.z.tar.gz` (portable canonical artifact bundle)
- `dist/linux/dominium-x.y.z.deb`
- `dist/linux/dominium-x.y.z.rpm`

## Tooling

Required (installed separately; not downloaded by the pipeline):

- `.deb`: `dpkg-deb`
- `.rpm`: `rpmbuild`

## Build

Run on Linux:

```
SOURCE_DATE_EPOCH=946684800 REPRODUCIBLE=1 make package-linux BUILD_DIR=build/<your-build> VERSION=x.y.z
```

Artifacts land in `dist/linux/`.

## FHS mapping (spec)

The package-managed artifacts stage the canonical layout under:

- `/opt/dominium/artifact_root/`  (contains `setup/`, `payloads/`, `docs/`)

The actual install root used by Setup Core is defined by the embedded `product.dsumanifest`.

Installed-state path (by convention):

- `<install_root>/.dsu/installed_state.dsustate`

## Maintainer scripts (rule)

Maintainer scripts may only invoke Setup Core (`dominium-setup`), and must be headless-safe.

Implemented scripts:

- deb: `scripts/packaging/linux/deb/DEBIAN/postinst`, `prerm`, `postrm`
- rpm: `%post`, `%preun` in `scripts/packaging/linux/rpm/dominium.spec.in`

## Portable tarball

The portable tarball is a deterministic archive containing:

```
artifact_root/*
```

It does not download anything; it is an offline artifact bundle.

Convenience wrapper (generated alongside the tarball):

- `dist/linux/dominium-install.sh`

## Sources

- Pipeline entry: `scripts/packaging/pipeline.py` (`linux` subcommand)
- deb templates: `scripts/packaging/linux/deb/DEBIAN/*`
- rpm template: `scripts/packaging/linux/rpm/dominium.spec.in`
