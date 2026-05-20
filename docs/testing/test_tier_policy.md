Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none

# Dominium Test Tier Policy

Dominium uses explicit proof tiers so routine development does not depend on a
slow full CTest run, while full CTest remains a real release and trust gate.

The machine-readable contract is:

- `contracts/testing/test_tiers.contract.toml`
- `contracts/testing/test_tiers.schema.json`

The validator is:

```text
python tools/validators/testing/check_test_tiers.py --repo-root . --strict
```

## T0 - Static Format and Repo Hygiene

T0 catches malformed files and accidental generated-output staging before
heavier checks run.

It includes:

- `git diff --check`
- staged generated/local output checks
- changed JSON/JSONL parsing
- changed TOML parsing
- forbidden top-level `src/`, `source/`, `sources`, and `common_source` roots

T0 failures are not accepted as warnings.

## T1 - Strict Repo and Contract Hygiene

T1 proves the repo remains inside the canonical ownership and contract spine.

It includes:

- AIDE doctor, validate, tools validate, roots validate, and repo validate
- strict repo layout, root allowlist, distribution layout, and component matrix
  validators
- no-`src`/`source` and forbidden-root validators
- docs sanity, include sanity, build target boundaries, UI shell purity, and ABI
  boundary checks
- C17/C++17 language baseline and macOS 10.9 C++17 library-subset validators
- the test-tier contract validator
- RepoX STRICT

Directory naming remains advisory where current repo debt is already classified.
Advisory findings must be reported; they do not convert required failures into
passes.

## T2 - Build and Smoke Proof

T2 proves the normal verify build/smoke loop still works.

It includes:

- `cmake --preset verify`
- `cmake --build --preset verify --target ALL_BUILD`
- smoke CTest through `ctest --preset verify -L smoke --output-on-failure --timeout 300`

T2 is the last tier in the normal development gate.
The build step intentionally uses `ALL_BUILD` so `fast_strict` does not invoke
the broader `verify_fast` target and then duplicate CTest selections. The
`verify_fast` CMake target remains available for its existing smoke,
portability, and buildmeta label set.

Focused schema/pack/content CTest and public-header consumer checks are T4 debt
until they are green and proven suitable for normal edit-loop runtime.

## T3 - Product and Projection Proof

T3 is not part of normal fast strict development. It is used for release,
projection, product command, and internal pilot evidence.

It includes:

- product boot matrix strict smoke
- portable projection strict validation
- internal pilot release strict validation

The projection and release roots are local ignored proof outputs. Missing or
stale roots block release proof; they do not block routine edit-loop work.

## T4 - Full, Release, and Trust Proof

T4 is the slow confidence lane.

It includes:

- selected AuditX slow shard for release candidate proof
- full CTest for full certification
- full verify build target where available
- legacy full-promotion wrapper evidence

T4 is where compatibility corpus, public-header consumer, replay determinism,
save migration, pack/mod trust, provider conformance, release promotion,
full package/FAB validation, performance, and portability checks belong as they
are wired or stabilized.

## Gates

`fast_strict` is T0 + T1 + T2:

```text
python tools/test/run_fast_strict.py --repo-root .
```

`extended` is T0 + T1 + T2 + relevant T3:

```text
python tools/test/run_fast_strict.py --repo-root . --gate extended
```

`release` is T0 + T1 + T2 + T3 + selected T4:

```text
python tools/test/run_fast_strict.py --repo-root . --gate release
```

`release_candidate` remains available as a compatibility alias for older task
packets.

`full` is all available T0 + T1 + T2 + T3 + T4:

```text
python tools/test/run_fast_strict.py --repo-root . --gate full
```

Full CTest is intentionally not the normal development gate. A full CTest
failure is still real debt and must remain visible until the full gate is green.

## Warning And Timeout Policy

Required command failures fail the selected gate. Optional command failures are
warnings only when the contract marks the command optional. Warnings must remain
visible in JSON and Markdown evidence.

The normal gate target is under 600 seconds. If a check cannot meet normal-gate
runtime or stability expectations, move it to T3 or T4 with rationale.

## Full-Gate Debt Policy

T4 debt must be tracked, not hidden. Full CTest, public-header consumer tests,
compatibility corpus, replay determinism, save migration, pack/mod trust,
provider conformance, release promotion, and broad portability/performance
checks belong in T4 until they are green and promoted by policy.

No test may be deleted, renamed, skipped, or reclassified solely to make a gate
green. A gate may pass only for the scope it declares. A green `fast_strict`
result is not evidence that full CTest or the release/full proof lane is green.
