Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00
Machine-Readable Source: `contracts/repo/naming.contract.toml`

# No `src` Or `source` Policy

Dominium does not use a root `src/` model.

The historical `docs/restructure/FUTURE_LAYOUT_PROPOSAL.md` still contains a proposed `/src` tree, but that document explicitly says the proposed `/src` layout is historical planning input and does not override the completed CONVERGE source-root model.

The active model is ownership-first:

```text
apps/
engine/
game/
runtime/
contracts/
content/
docs/
tests/
tools/
scripts/
cmake/
external/
release/
archive/
```

## Forbidden New Directories

Do not create:

```text
src/
source/
sources/
```

This applies both at repository root and under active ownership roots. These names hide ownership and make future moves ambiguous.

## Existing Historical Pockets

Existing tracked `source` or `src` path segments are classified as:

- historical or quarantined material under `archive/`, or
- transitional content identity debt under active bad-root exceptions, such as `packs/source/**`.

They are not current naming authority.

NAME-00 records this debt but does not move, delete, rename, rewrite, or retire it.

## Source Repo Is Not Install Layout

Distribution, package, media, runtime-store, save, instance, cache, staging, rollback, and portable install layouts are projections governed by `contracts/distribution/layout.contract.toml`.

Those projection names must not be copied into source roots. In particular, source cleanup must not introduce active roots such as:

```text
store/
instances/
saves/
exports/
cache/
ops/
media/
runtime-store/
```

## Future Enforcement

The initial validator is warning-oriented because existing debt remains. It becomes a hard blocker for new unexcepted `src`, `source`, or `sources` directories outside `archive/` and active exception roots.
