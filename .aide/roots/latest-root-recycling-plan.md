# Root Recycling Plan

- plan_id: q40-root-recycling-no-apply-plan
- status: dry_run
- source_commit: 80dc7bfb58a1cdc887ee1fed8a83fb22ff3028e0
- risk_class: high
- no_apply: true
- file_moves: false
- file_deletes: false
- reference_rewrites: false
- target_repo_mutation: false

## Recommended Sequence

- inventory
- classify
- plan
- review
- future_salvage_map
- future_move_map
- future_alias_plan
- future_apply
- future_validate
- future_retire_exception

## Root Plans

- `.aide`: risk=high status=mixed review_files=249
- `.aide.local.example`: risk=high status=review_required review_files=5
- `.github`: risk=high status=review_required review_files=2
- `.vscode`: risk=high status=review_required review_files=1
- `apps`: risk=high status=mixed review_files=273
- `archive`: risk=high status=review_required review_files=1235
- `artifacts`: risk=high status=review_required review_files=10
- `bundles`: risk=high status=review_required review_files=3
- `cmake`: risk=high status=review_required review_files=33
- `compat`: risk=high status=review_required review_files=17
- `content`: risk=high status=review_required review_files=3
- `contracts`: risk=high status=review_required review_files=1613
- `control`: risk=high status=review_required review_files=21
- `core`: risk=high status=review_required review_files=16
- `data`: risk=high status=review_required review_files=1279
- `dist`: risk=high status=review_required review_files=13
- `docs`: risk=medium status=mixed review_files=4050
- `engine`: risk=high status=mixed review_files=669
- `game`: risk=high status=mixed review_files=918
- `governance`: risk=high status=review_required review_files=2
- `ide`: risk=high status=review_required review_files=4
- `lib`: risk=high status=review_required review_files=22
- `libs`: risk=high status=review_required review_files=86
- `locks`: risk=high status=review_required review_files=1
- `meta`: risk=high status=review_required review_files=26
- `modding`: risk=high status=review_required review_files=2
- `models`: risk=high status=review_required review_files=2
- `net`: risk=high status=review_required review_files=17
- `packs`: risk=high status=mixed review_files=256
- `performance`: risk=high status=review_required review_files=3
- `profiles`: risk=high status=review_required review_files=1
- `release`: risk=high status=review_required review_files=6
- `repo`: risk=high status=review_required review_files=11
- `repo-root`: risk=high status=mixed review_files=30
- `runtime`: risk=high status=review_required review_files=52
- `safety`: risk=high status=review_required review_files=2
- `scripts`: risk=high status=mixed review_files=48
- `security`: risk=high status=review_required review_files=4
- `specs`: risk=high status=review_required review_files=9
- `templates`: risk=high status=review_required review_files=2

## Blocked Reasons

- .aide: high
- .aide.local.example: high
- .github: high
- .vscode: high
- apps: high
- archive: high
- artifacts: high
- bundles: high
- cmake: high
- compat: high
- content: high
- contracts: high
- control: high
- core: high
- data: high
- dist: high
- engine: high
- game: high
- governance: high
- ide: high
- lib: high
- libs: high
- locks: high
- meta: high
- modding: high
- models: high
- net: high
- packs: high
- performance: high
- profiles: high
- release: high
- repo: high
- repo-root: high
- runtime: high
- safety: high
- scripts: high
- security: high
- specs: high
- templates: high
- tests: high
- tools: high
- updates: high
- validation: high

## Boundary

- Q40 plans only. It does not move roots, delete files, rewrite references, absorb tools, or apply maps.
