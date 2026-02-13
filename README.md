# Dominium / Domino

Deterministic simulation platform and product stack built around a data-first architecture, explicit authority, and reproducible execution.

![Build](https://img.shields.io/badge/build-verify%20preset-blue)
![Languages](https://img.shields.io/badge/language-C89%20%2F%20C%2B%2B98-critical)
![Governance](https://img.shields.io/badge/governance-RepoX%20%7C%20TestX%20%7C%20AuditX-purple)
![Coverage](https://img.shields.io/badge/coverage-TestX%20suites-informational)

## What Dominium Is

Dominium is the product layer (Client, Server, Launcher, Setup, Tools) on top of the Domino simulation engine. The repository is governed by explicit contracts:

- **Ontology**: Assemblies / Fields / Processes / Agents / Law
- **Determinism**: same canonical inputs produce the same canonical outputs
- **Authority**: all mutations route through process execution under `AuthorityContext`
- **Data-first extensibility**: schemas + registries + packs define behavior surfaces

See `docs/ARCHITECTURE.md` for the technical model.

## High-Level Architecture

- **Engine (`engine/`)**: deterministic simulation substrate (C89)
- **Game (`game/`)**: meaning/rules layer on engine APIs (C++98)
- **Client (`client/`)**: presentation and command projection
- **Server (`server/`)**: authoritative multiplayer/session enforcement
- **Governance (`repo/`, `tests/`, `tools/*x/`)**: RepoX/TestX/AuditX/XStack

Canonical architecture contracts are under `docs/architecture/`, starting at `docs/architecture/ARCH0_CONSTITUTION.md`.

## Quick Start (Windows Verify Lane)

Prerequisites:

- CMake (see `docs/guides/BUILDING.md`)
- Python 3.x for governance scripts
- Verify preset toolchain configured

Build:

```bash
cmake --preset verify
cmake --build --preset verify
```

Run governance gate:

```bash
python scripts/dev/gate.py verify --repo-root .
```

Run binaries from verify output:

```bash
out\build\vs2026\verify\bin\client.exe --ui=none --smoke
out\build\vs2026\verify\bin\server.exe --help
out\build\vs2026\verify\bin\launcher.exe --help
out\build\vs2026\verify\bin\tools.exe --help
```

## Key Documentation

- Architecture: `docs/ARCHITECTURE.md`
- Governance stack: `docs/XSTACK.md`
- Survival vertical slice: `docs/SURVIVAL_SLICE.md`
- Canon index: `docs/architecture/CANON_INDEX.md`
- Glossary: `docs/GLOSSARY.md`
- Status snapshot: `docs/STATUS_NOW.md`

## Governance Stack Overview

Execution and enforcement layers:

- **RepoX** static invariants (`docs/governance/REPOX_RULESETS.md`)
- **TestX** behavioral proof (`docs/governance/TESTX_ARCHITECTURE.md`)
- **AuditX** semantic drift analysis (`docs/governance/AUDITX_MODEL.md`)
- **XStack gate** FAST/STRICT/FULL execution (`docs/governance/GATE_THROUGHPUT_POLICY.md`)

## Contributing

Contribution workflow, coding standards, schema/registry updates, and gate usage are documented in `CONTRIBUTING.md`.

## Survival Baseline

The deterministic minimal survival slice, including needs, hazards, shelter, and diegetic lens constraints, is documented in `docs/SURVIVAL_SLICE.md`.

## More Detailed Docs

- Docs entry: `docs/README.md`
- Product docs: `DOMINIUM.md`
- Modding guidance: `MODDING.md`
- Security policy: `SECURITY.md`

## License / Contact

- License: `LICENSE.md`
- Security contact/process: `SECURITY.md`
