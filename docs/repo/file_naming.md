Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00
Machine-Readable Source: `contracts/repo/naming.contract.toml`

# File Naming

File names encode artifact role, not temporary status.

The default for new files is:

```text
lower_snake_case.ext
```

Avoid status, era, and uncertainty words in active filenames:

```text
new
old
future
modern
classic
legacy
universal
misc
tmp
draft
final_final
v2
```

Use role suffixes where the file participates in a contract, registry, manifest, proof, report, or audit surface.

| Role | Pattern |
| --- | --- |
| Schema | `*.schema.json` |
| Registry | `*.registry.json` |
| Manifest | `*.manifest.json` |
| Contract | `*.contract.toml` |
| Policy | `*.policy.toml` |
| Matrix | `*.matrix.toml` or `*_matrix.contract.toml` |
| Lock | `*.lock.json` |
| Proof | `*.proof.json` |
| Report | `*.report.md` or `*.report.json` |
| Audit | `*.audit.md` or `*.audit.json` |

## Conventional Exceptions

Tool-recognized and repo-root conventional names remain allowed:

```text
README.md
LICENSE
LICENSE.md
CHANGELOG.md
SECURITY.md
CONTRIBUTING.md
AGENTS.md
CLAUDE.md
CMakeLists.txt
CMakePresets.json
VERSION_*
```

Existing uppercase audit, evidence, and planning docs are transitional debt and may stay until a doc-only normalization pass. Do not mix broad doc renames with root moves or semantic changes.

The 2026-05-18 NAME-00 redo records 5,361 file-name findings, 4,307 warnings, and 0 blockers. Most warnings are existing uppercase docs, noncanonical historical/evidence names, or hyphenated filenames that predate the canon. They are not accepted as final style, and they are not renamed by NAME-00.

## Code Files

Use module nouns:

```text
clock.c
clock.h
state_store.c
state_store.h
renderer.c
renderer.h
platform_probe.c
platform_probe.h
```

Tests should make their role explicit:

```text
clock_test.c
state_store_test.c
test_package_manifest.py
test_repo_layout.py
```

## Contract Identity

Contracts and manifests define identity. Paths are storage.

Do not change contract IDs, package IDs, product IDs, pack IDs, profile IDs, bundle IDs, save IDs, ABI IDs, or release IDs merely because a file is moved in a future migration.

Future move tasks must preserve identity values unless an explicit doctrine or contract-update task authorizes a meaning change.
