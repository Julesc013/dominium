# AIDE Latest Context Packet

## CONTEXT_COMPILER

- compiler: q11-context-compiler-v0
- generator: aide-lite
- generator_version: q24.existing-tool-adapter-compiler.v0
- contents_inline: false
- method: deterministic repo-local metadata, roles, priorities, and test heuristics

## SOURCE_REFS

- `.aide/context/compiler.yaml`
- `.aide/context/priority.yaml`
- `.aide/context/excerpt-policy.yaml`
- `.aide/context/ignore.yaml`
- `.aide/context/dominium-doctrine-refs.md` (present)
- `.aide/context/repo-snapshot.json`
- `.aide/context/context-index.json`
- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`

## REPO_MAP

- json: `.aide/context/repo-map.json`
- markdown: `.aide/context/repo-map.md`
- file_count: 13577
- source_snapshot_hash: `c199dfef48ec5cbe868dea80ba8584f7103d4864644e6de04e2a3246a6512b7e`

## ROLE_COUNTS

- aide_contract: 26
- aide_policy: 28
- aide_prompt: 3
- aide_context: 5
- aide_queue: 1
- test: 2127
- docs: 4065
- governance: 2
- script: 49
- config: 2282
- unknown: 4989

## TEST_MAP

- path: `.aide/context/test-map.json`
- mapping_count: 4178
- mappings_with_existing_candidate: 1
- complete_coverage_claimed: false

## CURRENT_QUEUE

- current_queue_ref: `.aide/queue/index.yaml`
- queue_index: `.aide/queue/index.yaml`

## EXACT_REFS

- Preferred syntax: `path#Lstart-Lend`
- Validate refs before use.
- Do not inline whole files by default.
- Never inline ignored files, secrets, local state, caches, or binary artifacts.

## PACKET_GUIDANCE

- Use repo-map and test-map refs before broad documentation dumps.
- Include exact line refs only when required for correctness.
- Ask for additional context only when the compact packet is insufficient.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 1865
- approx_tokens: 467
- formal ledger: `.aide/reports/token-ledger.jsonl`
