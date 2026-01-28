# Repo Ownership and Projections (REPOX)

Status: binding.
Scope: repository sovereignty, authoritative sources, and IDE projections.

## Canonical statements
- CMake + TESTX/2/3 define the build graph and testing truth.
- IDE projects are projections only; they are never authoritative.
- Projections live under `/ide/**` and are disposable.

## Classification (authoritative vs projection vs frozen)
| Path / Pattern | Class | Owner / Notes |
| --- | --- | --- |
| `/CMakeLists.txt`, `/cmake/**` | AUTHORITATIVE | Build graph and toolchain policy. |
| `/engine/**`, `/game/**` | AUTHORITATIVE | Core simulation and game meaning. |
| `/client/**`, `/server/**` | AUTHORITATIVE | Application shells and network services. |
| `/launcher/**`, `/setup/**`, `/tools/**` | AUTHORITATIVE | Tools and installers (logic only). |
| `/libs/**`, `/schema/**`, `/data/**` | AUTHORITATIVE | Contracts, schemas, and data. |
| `/docs/**`, `/scripts/**`, `/ci/**`, `/.github/**` | AUTHORITATIVE | Canon, policy, and CI enforcement. |
| `/legacy/**` | AUTHORITATIVE (archival) | Historical sources; not part of current build graph. |
| `/ide/**` | GENERATED / PROJECTION | Disposable IDE outputs. |
| `/ide/README.md`, `/ide/manifests/**` | AUTHORITATIVE metadata | Projection policy + manifest schema/examples. |
| `/setup/**/package/**/vs/**` | FROZEN PACKAGING INPUT | Grandfathered packaging inputs (none currently). |
| `/setup/**/xcode/**` | FROZEN PACKAGING INPUT | Grandfathered packaging inputs (none currently). |
| `/.vs`, `/.vscode` | GENERATED | Local IDE state; must never be committed. |
| `/build/**`, `/dist/**`, `/out/**`, `/bin/**` | GENERATED | Build outputs. |

## Grandfathered packaging inputs
None discovered in the repository at the time of REPOX survey.
If any are added later, they MUST be listed here with exact paths.

## Forbidden IDE actions
- Opening the repo root in legacy IDEs and letting them auto-add files.
- Committing IDE output outside `/ide/**` or grandfathered packaging inputs.
- Editing generated projections by hand (regenerate instead).
- Upgrading toolchains or SDKs silently via IDE prompts.

## Regeneration expectations
- IDE projections MUST be deterministic and reproducible.
- Deleting `/ide/**` is safe; regenerate via `scripts/ide_gen.*`.

## Cross-references
- `docs/architecture/PROJECTION_LIFECYCLE.md`
- `docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md`
- `docs/policies/IDE_CONTRIBUTION_RULES.md`
