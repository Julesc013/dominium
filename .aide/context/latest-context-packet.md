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
- `.aide/context/repo-snapshot.json`
- `.aide/context/context-index.json`
- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`

## REPO_MAP

- json: `.aide/context/repo-map.json`
- markdown: `.aide/context/repo-map.md`
- file_count: 37166
- source_snapshot_hash: `29e7515d53d64c3f72512d2d4cf4d3451f1eab4f0b2de6b4f4114a95ead59950`

## ROLE_COUNTS

- aide_contract: 274
- aide_policy: 117
- aide_prompt: 3
- aide_context: 5
- aide_queue: 442
- aide_evidence: 490
- test: 3928
- docs: 6320
- script: 49
- config: 9459
- generated: 9
- unknown: 16070

## TEST_MAP

- path: `.aide/context/test-map.json`
- mapping_count: 7162
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
- chars: 1836
- approx_tokens: 459
- formal ledger: `.aide/reports/token-ledger.jsonl`
