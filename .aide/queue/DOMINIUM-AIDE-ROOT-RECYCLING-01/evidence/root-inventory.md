# Root Inventory

Status: needs_review

## Roots Inspected

- Full AIDE root inventory: 44 roots, 15,977 tracked files.
- Selected pilot root: `ide/`.

## Selected Root File Counts

- Tracked files: 4.
- Untracked files under `ide/`: none reported by `git status --ignored --short ide`.
- Ignored generated paths are governed by `.gitignore` rules for `/ide/**` with exceptions for `ide/README.md` and `ide/manifests/**`.

## Selected Root Kinds

Dominium Q52 overlay classification:

- `doc`: 1
- `schema`: 1
- `fixture`: 2

Baseline AIDE classification for `ide/`:

- `doc`: 1
- `schema`: 1
- `unknown`: 2

## Generated / Evidence / Source / Test / Tool / Policy / Schema Counts

For selected root:

- generated-sensitive fixtures: 2
- evidence-only: 0
- product source: 0
- tests: 0
- tools: 0
- policy-like README: 1
- schema: 1
- unknown after Dominium overlay: 0

## Caveats

The root remains `review_required` because `ide/README.md` is binding root policy and `projection_manifest.schema.json` is schema identity. The two examples are not disposable; they are tracked fixtures under the preserved manifest exception.
