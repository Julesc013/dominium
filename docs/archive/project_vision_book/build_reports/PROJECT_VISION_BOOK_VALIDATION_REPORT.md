Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Roots: `docs/archive/project_vision_corpus/`; `tmp/project_vision_corpus/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Project Vision Book Validation Report

## Generated Checks

- External corpus inspected: yes
- Committed corpus inspected: yes
- Output files generated: 36
- Current reality vs long-horizon separated: yes
- Contradictions preserved: yes
- No archive claim promoted to canon: yes
- Existing committed corpus overwritten: no
- Evidence/source-block IDs exposed in main book: no
- Banned machine-report patterns in main book: none

## External Commands

| Command | Result | Notes |
| --- | --- | --- |
| `py -3 -m py_compile tools/docs_corpus/build_project_vision_book.py` | PASS | Builder parses. |
| `py -3 -m unittest tests/tools/docs_corpus/test_project_vision_book.py` | PASS | Main book substance and banned-pattern tests passed. |
| `py -3 tools/docs_corpus/build_project_vision_book.py --repo-root . --repo-corpus-root docs/archive/project_vision_corpus --external-corpus-root tmp/project_vision_corpus --output-root docs/archive/project_vision_book` | PASS | Generated 36 files; main book 4,051 words. |
| `py -3 -m unittest tests/tools/docs_corpus/test_project_vision_corpus.py tests/tools/docs_corpus/test_project_vision_corpus_comparison.py tests/tools/docs_corpus/test_project_vision_book.py` | PASS | 12 tests passed. |
| `py -3 tools/conversations/validate_conversation_outputs.py --repo-root .` | PASS | Existing conversation outputs valid. |
| `py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root .` | PASS_WITH_WARNINGS | Pre-existing generated-header warnings under `docs/archive/docs_corpus/**`, outside this task output root. |
| main book banned-pattern check | PASS | No evidence-card/source-block IDs or old machine-report headings in main book. |
| `git diff --check` | PASS | No whitespace errors. |
| protected path check | PASS | No canon, architecture, contracts, schema, implementation, release, or queue paths changed. |
| existing committed corpus overwrite check | PASS | No unstaged/staged diff under `docs/archive/project_vision_corpus/**`. |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS | AIDE doctor passed. |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS | AIDE validate passed. |

## Warning Scope

The only warning class observed was from the existing docs-corpus validator, which reports older generated markdown files under `docs/archive/docs_corpus/**` missing derived headers near the top. Those files predate this task and are outside `docs/archive/project_vision_book/**`.

## Impact Statements

- Canon impact: unchanged.
- Contract/schema impact: unchanged.
- Implementation impact: unchanged.
- Release impact: unchanged.
- Queue impact: unchanged.
- Archive/conversation claim promotion: none.
- Protected path changes: none.
