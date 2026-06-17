Status: DERIVED
Last Reviewed: 2026-06-17
Supersedes: legacy top-level `CONTRIBUTING.md` workflow summary
Superseded By: none
Stability: provisional
Future Series: PUBLIC-DOCS
Replacement Target: long-lived contributor entrypoint derived from canon, AGENTS, contracts, status, build docs, and legal contribution terms

# Contributing to Dominium

This document is the public contributor entrypoint for code, documentation,
content, contract, schema, tooling, and governance changes in this repository.

It is derived. If this file conflicts with `docs/canon/constitution_v1.md`,
`docs/canon/glossary_v1.md`, `AGENTS.md`, active contracts, `.aide/queue/current.toml`,
or reviewed audits, the higher-authority artifact wins for project, technical,
canon, architecture, validation, and governance meaning.

Legal files control legal permissions and restrictions. `LICENSE.md`,
`CONTRIBUTOR_LICENSE_AGREEMENT.md`, `TRADEMARKS.md`, `FAN_CONTENT_POLICY.md`,
and `THIRD_PARTY_NOTICES.md` are not overridden by canon, contracts, queue state,
architecture docs, generated summaries, issue comments, or pull request comments.

## Before You Start

Dominium is not a conventional "just patch the code" repository. Most useful
changes sit inside a governed architecture model:

- canon defines non-negotiable invariants
- contracts and registries define public law
- code implements lawful behavior
- tests, validators, diagnostics, evidence, and audits prove claims
- public docs explain the current state without overclaiming

Read first:

1. `README.md`
2. `LICENSE.md`
3. `CONTRIBUTOR_LICENSE_AGREEMENT.md`
4. `docs/STATUS.md`
5. `docs/ARCHITECTURE.md`
6. `AGENTS.md`
7. the relevant contract, registry, architecture, test, or content files for
your change

## Legal Terms For Contributors

Dominium is source-available and restricted-use. It is not an open source project
under OSI-style open source terms.

By submitting any pull request, patch, issue attachment, documentation change,
content, schema, contract, test, fixture, tool, asset, generated output, or other
material for possible inclusion in Dominium, you agree to
`CONTRIBUTOR_LICENSE_AGREEMENT.md`.

Do not submit a contribution unless:

1. you have read and agree to `CONTRIBUTOR_LICENSE_AGREEMENT.md`;
2. you created the contribution or have all rights needed to submit it;
3. your employer, client, school, or other organisation does not own or restrict
   the contribution, or has authorised submission under the CLA;
4. all third-party material is clearly identified with source, license, and
   compatibility information;
5. any generated, AI-assisted, copied, adapted, or tool-produced material is
   clearly identified where required and can be assigned or licensed under the
   CLA;
6. you understand that accepted contributions may be assigned or exclusively
   licensed to the Project Owner and may be used, modified, commercialised,
   withheld, removed, or relicensed by the Project Owner.

Submitting a contribution does not grant you permission to publish, distribute,
maintain, monetise, host, or promote an independent fork, modified version,
server, pack, tool, engine, game, product, or derivative work. Your use of the
repository remains governed by `LICENSE.md`.

## Current Public Boundary

The current status does not authorize broad feature work. The queue keeps broad
Workbench UI, runtime module loading, provider runtime, package runtime,
gameplay, renderer implementation, native GUI, and release publication blocked
until reviewed phases explicitly open them.

Contributions should therefore be narrow, evidence-backed, and aligned with the
current queue or with a clearly scoped documentation/content/validation target.

## Task Shape

Use this shape when proposing or executing work:

```text
Task:
Goal:
Touched Paths:
Relevant Invariants:
Contracts/Schemas:
Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Non-Goals:
```

This is the same operating shape used by `AGENTS.md`. It keeps scope explicit
and prevents accidental architecture drift.

## Repository Structure

Primary roots:

| Root | Meaning |
|---|---|
| `apps/` | Thin product entrypoints and product composition. |
| `engine/` | Domino deterministic substrate and public engine-facing surfaces. |
| `game/` | Dominium domain rules, process emission, and game interpretation. |
| `runtime/` | Shell, platform, view, diagnostics, storage, input, audio, network, and host integration. |
| `contracts/` | Machine-readable, version-pinned, compatibility-sensitive law. |
| `content/` | Authored packs, profiles, datasets, fixtures, assets, templates, and source payloads. |
| `docs/` | Canon, architecture, development, reference, planning, release, repo, and archive documentation. |
| `tests/` | Contract, invariant, smoke, integration, fixture, and proof suites. |
| `tools/` | Validation, codegen, migration, packaging, audit, release, and developer tooling. |
| `.aide/` | Queue, context, memory, scripts, and AIDE-local repo operation surfaces. |
| `archive/` | Historical, superseded, quarantined, or provenance-retained material. |

Do not infer ownership from similarly named roots. Follow `AGENTS.md`, layout
contracts, and scope-specific artifacts before binding work to transitional,
projected, or quarantined paths.

## Workflow For Code Changes

1. Identify the governing canon, contract, registry, schema, and owning root.
2. Confirm the change is authorized by the current queue or by explicit task
scope.
3. Update contracts/registries before or with behavior changes when public shape,
compatibility, diagnostics, refusal semantics, commands, modules, providers, or
artifact identity changes.
4. Preserve determinism, process-only mutation, truth/perceived/render
separation, profile-driven composition, explicit refusals, and pack-driven
integration.
5. Add or update relevant tests, validators, fixtures, or audit material.
6. Update docs in the same change when behavior or public meaning changes.
7. Report what validation was run and what was not run.

## Workflow For Documentation Changes

Documentation changes are still governed work. They must not promote planned or
blocked features into implemented claims.

When changing public docs:

1. Check `docs/STATUS.md` and `.aide/queue/current.toml`.
2. Keep `README.md` as the public front door.
3. Put current truth boundaries in `docs/STATUS.md`.
4. Put future sequencing in `docs/ROADMAP.md`.
5. Put architecture explanation in `docs/ARCHITECTURE.md`.
6. Put product meaning in `DOMINIUM.md`.
7. Do not edit canon merely to make public prose easier.

## Build And Verify

Normal public verification path:

```powershell
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
py -3 tools/test/run_fast_strict.py --repo-root .
```

AIDE local health checks:

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
```

Targeted validators for common contract surfaces:

```powershell
py -3 tools/validators/repo/check_dependency_directions.py --repo-root . --strict
py -3 tools/validators/contracts/check_command_surface.py --repo-root . --strict
py -3 tools/validators/contracts/check_module_descriptors.py --repo-root . --strict
py -3 tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict
```

Fast strict is the normal development gate. Extended, release, and full proof
tiers are separate gates defined by `contracts/testing/test_tiers.contract.toml`.
Do not claim full certification from a green fast strict result.

## Language And ABI Constraints

- C code uses C17.
- C++ code uses C++17.
- Stable public binary-facing surfaces remain C-compatible.
- Do not expose C++ classes, STL types, exceptions, RTTI, allocator objects, or
compiler object layout across stable ABI boundaries.

See:

- `docs/development/LANGUAGE_BASELINE.md`
- `docs/development/C17_USAGE_POLICY.md`
- `docs/development/CPP17_USAGE_POLICY.md`
- `contracts/abi/c_api.contract.toml`
- `contracts/abi/language_boundary.contract.toml`

## Determinism Requirements

All accepted implementation changes must preserve deterministic behavior:

- no wall-clock or anonymous random side effects in authoritative paths
- stable ordering for canonical artifacts and execution outcomes
- named RNG streams for authoritative randomness
- explicit refusal codes for invalid, unsupported, or incompatible transitions
- deterministic migration, replay, hashing, and evidence behavior where the
relevant contract requires it

## Content And Pack Contributions

Content is authored data, not runtime law. Packs and modding are data-first and
contract-governed.

Start with:

- `MODDING.md`
- `content/README.md`
- `content/packs/README.md`
- `contracts/package/packs/README.md`
- `contracts/capability/README.md`

Do not introduce arbitrary executable pack code or hidden fallback behavior.
Missing optional content must degrade or refuse explicitly.

Pack/content contributions are still contributions under
`CONTRIBUTOR_LICENSE_AGREEMENT.md`. Do not submit third-party assets, data,
fonts, audio, images, models, generated output, or copied material without clear
provenance and compatible rights.

## Pull Request Checklist

Before submitting or merging work, check:

- [ ] I have read and agree to `CONTRIBUTOR_LICENSE_AGREEMENT.md`.
- [ ] I have the right to submit this contribution under the CLA.
- [ ] This contribution does not include third-party code, assets, data, or generated output unless clearly identified.
- [ ] I understand accepted contributions may be used, modified, commercialised, withheld, removed, assigned, exclusively licensed, or relicensed by the Project Owner.
- [ ] I understand this contribution does not grant me permission to publish, distribute, monetise, host, or maintain an independent fork or derivative version of Dominium.
- [ ] Scope matches the current task, queue, or explicit issue.
- [ ] Relevant invariants are named.
- [ ] Contract/schema/registry impact is stated.
- [ ] Determinism impact is stated.
- [ ] Public docs were updated if public behavior or meaning changed.
- [ ] New claims are evidenced by code, contract, tests, queue state, or audit.
- [ ] Planned or blocked features are not described as implemented.
- [ ] Appropriate validators/tests were run, or non-runs are reported.
- [ ] Generated outputs are treated as evidence unless explicitly promoted.

## Protected Areas

Extra review discipline is required for changes touching:

- `docs/canon/**`
- `AGENTS.md`
- `docs/planning/**`
- `contracts/**` when public law or compatibility meaning changes
- release, publication, trust, security, licensing, or public policy surfaces
- ownership-sensitive or quarantined roots described by `AGENTS.md`

Protected does not mean untouchable. It means scope, authority, and provenance
must be explicit.
