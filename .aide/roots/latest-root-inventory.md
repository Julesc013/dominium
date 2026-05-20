# Latest Root Inventory

- generated_by: aide-lite
- source_commit: e201f72d6825c5f815f3850692885ed185745b6b
- source_mode: repo_intelligence_index_plus_tracked_delta
- file_count: 17622
- root_count: 18
- no_apply: true
- file_moves: false
- file_deletes: false
- reference_rewrites: false
- provider_or_model_calls: none
- network_calls: none
- next_phase: Q41 Existing Tool Absorption v0

## Root Status Counts

- mixed: 9
- review_required: 9

## Root Risk Counts

- high: 18

## Roots

- `.aide`: files=1571 status=mixed risk=high
- `.aide.local.example`: files=5 status=review_required risk=high
- `.github`: files=2 status=review_required risk=high
- `.vscode`: files=1 status=review_required risk=high
- `apps`: files=158 status=mixed risk=high
- `archive`: files=2174 status=review_required risk=high
- `cmake`: files=34 status=review_required risk=high
- `content`: files=730 status=mixed risk=high
- `contracts`: files=2229 status=review_required risk=high
- `docs`: files=4203 status=mixed risk=high
- `engine`: files=266 status=review_required risk=high
- `game`: files=909 status=review_required risk=high
- `release`: files=84 status=mixed risk=high
- `repo-root`: files=30 status=mixed risk=high
- `runtime`: files=386 status=mixed risk=high
- `scripts`: files=51 status=mixed risk=high
- `tests`: files=1104 status=mixed risk=high
- `tools`: files=3685 status=review_required risk=high

## Warnings

- unknown_or_unknown-owner_root_candidates: .aide.local.example, .github, .vscode, apps, archive, cmake, content, contracts, docs, engine, game, release
- mixed_root_candidates: .aide, apps, content, docs, release, repo-root, runtime, scripts, tests
- high_risk_root_candidates: .aide, .aide.local.example, .github, .vscode, apps, archive, cmake, content, contracts, docs, engine, game
