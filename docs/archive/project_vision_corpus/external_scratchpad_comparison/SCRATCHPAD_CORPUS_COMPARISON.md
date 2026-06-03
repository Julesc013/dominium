Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_comparison
Source Root: `docs/archive/project_vision_corpus/`; `tmp/project_vision_corpus/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Scratchpad Corpus Comparison

## Assessment

The scratchpad corpus is a useful corroborating variant, not a replacement for the repo corpus. It appears to have run against an uploaded `dominium archives.zip` package outside the live repository. That explains its larger top-level zip count and its lack of live repo validation. The repo corpus ran against the checked-in conversation archive plus current authority docs and validators.

## Count Comparison

| Metric | Repo corpus | Scratchpad corpus |
| --- | ---: | ---: |
| Zip packages / extracted top-level zips | 30 | 47 |
| Human-readable sources selected | 221 | 160 |
| Semantic source blocks | 2086 | 2500 |
| Theme groups | 17 | 17 |
| Source basename overlap | 120 | 120 |
| Repo-only selected source basenames | 95 | n/a |
| Scratchpad-only selected source basenames | n/a | 40 |

## Interpretation

- The scratchpad selected fewer source files but produced more blocks, because it favored large full-chat and detailed report files from the uploaded archive.
- The repo selected more source files because it included current generated conversation synthesis, reader/wiki/reconciliation outputs, and current repo authority context.
- The scratchpad had stronger raw uploaded-package visibility, including 47 top-level zip packages and 56 top-level archive entries.
- The repo had stronger authority safety: current files were live-inspected, validators ran, protected paths were checked, and the generated output was committed.

## Synthesis Agreement

Both corpora converge on the same central picture: Dominium is the product-facing simulation/game/tool universe, Domino is the deterministic portable substrate, presentation and providers must remain replaceable projections, and archive material is advisory historical evidence rather than canon.

## Synthesis Differences

The scratchpad prose is more explicit about the long-horizon product ecosystem: launcher, setup, game, tools, Workbench/AIDE, content packs, providers, and world simulation. The repo synthesis is more conservative and more tightly tied to current queue blocks and authority boundaries.

## Recommendation

Keep the repo corpus as the active derived corpus. Use the scratchpad as a comparison source for the next synthesis refinement, especially for full-chat reports and uploaded-archive-only package context. Do not copy scratchpad claims into canon, contracts, implementation, release, or queue state.
