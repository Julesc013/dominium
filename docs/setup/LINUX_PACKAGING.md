# Linux Packaging (tar.gz + deb + rpm)

## Outputs

Linux packaging has two entry points:

- CMake targets (see below):
  - `dist/linux/Dominium-linux-<arch>-<version>.tar.gz`
  - `dist/linux/dominium_<version>_<arch>.deb`
  - `dist/linux/dominium-<version>-<release>.<arch>.rpm`
- Pipeline script (`scripts/packaging/pipeline.py linux`):
  - `dist/linux/dominium-<version>.tar.gz`
  - `dist/linux/dominium-<version>.deb`
  - `dist/linux/dominium-<version>.rpm`

## Tooling

Required (installed separately; not downloaded by the pipeline):

- `.deb`: `dpkg-deb`
- `.rpm`: `rpmbuild`

## Build (CMake targets)

Enable packaging targets and run on Linux:

```
cmake -S . -B build -DDOMINIUM_ENABLE_PACKAGING=ON
cmake --build build --target linux_tarball_<arch>
cmake --build build --target linux_deb_<arch>
cmake --build build --target linux_rpm_<arch>
cmake --build build --target package-linux
```

Artifacts land in `build/dist/linux/`.

## FHS mapping (spec)

The package-managed artifacts stage the canonical layout under:

- `/opt/dominium/artifact_root/`  (contains `setup/`, `payloads/`, `docs/`)

The actual install root used by Setup Core is defined by the embedded
`product.dsumanifest`. Package managers own the staged `artifact_root/` tree;
Setup Core owns the installed files, state, and logs under the chosen install
root.

Installed-state path (by convention):

- `<install_root>/.dsu/installed_state.dsustate`

## Maintainer scripts (rule)

Maintainer scripts may only invoke Setup Core (`dominium-setup`) using
invocation payloads, and must be headless-safe.

Implemented scripts:

- deb: `scripts/packaging/linux/deb/DEBIAN/postinst`, `prerm`, `postrm`
- rpm: `%post`, `%preun` in `scripts/packaging/linux/rpm/dominium.spec.in`

The current model treats `.deb`/`.rpm` as installer bundles: package install
stages `artifact_root/` and invokes Setup Core to populate the actual install
root and state. Package removal calls Setup Core uninstall first.

Registrations:

- `dominium-setup-linux platform-register --state <statefile>`
- `dominium-setup-linux platform-unregister --state <statefile>`

## Portable tarball

The portable tarball is a deterministic archive containing:

```
artifact_root/*
```

It does not download anything; it is an offline artifact bundle.

Convenience wrapper (generated alongside the tarball):

- `dist/linux/dominium-install.sh`

The wrapper writes a `dsu_invocation` payload for the selected scope and
invokes `dominium-setup export-invocation`, `dominium-setup plan`, and
`dominium-setup apply`. It uses `dominium-setup-linux` to register desktop
entries when available.

Supported wrapper flags:

- `--scope portable|user|system`
- `--install-root <path>`
- `--components <csv>` / `--exclude <csv>`

## Sources

- Pipeline entry: `scripts/packaging/pipeline.py` (`linux` subcommand)
- deb templates: `scripts/packaging/linux/deb/DEBIAN/*`
- rpm template: `scripts/packaging/linux/rpm/dominium.spec.in`
- installer suite templates: `source/dominium/setup/installers/linux/packaging/`
