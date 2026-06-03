Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Project Vision Corpus Validation Report

- Result: PASS
- Zip packages accounted for: 30
- Source files selected: 221
- Source blocks generated: 2086
- Themes generated: 17
- Protected path changes: none detected

## Commands

| Command | Result | Exit Code |
| --- | --- | ---: |
| parse ZIP_MANIFEST.json | PASS | 0 |
| protected path check | PASS | 0 |
| py -3 -m py_compile tools/docs_corpus/build_project_vision_corpus.py | PASS | 0 |
| py -3 -m unittest tests/tools/docs_corpus/test_project_vision_corpus.py | PASS | 0 |
| py -3 tools/conversations/validate_conversation_outputs.py --repo-root . | PASS | 0 |
| py -3 tools/docs_corpus/validate_docs_corpus_outputs.py --repo-root . | PASS_WITH_WARNINGS | 0 |
| git diff --check | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py doctor | PASS | 0 |
| py -3 .aide/scripts/aide_lite.py validate | PASS | 0 |

## Quality Gate

- Raw zips were read only, not modified.
- Current truth versus advisory vision is labelled in synthesis outputs.
- Archive/conversation claims remain advisory.
- No live-doc promotion was performed.
- No final book was generated in this milestone.
- Synthesis and review outputs were checked for visible block/evidence IDs and old machine-report headings.
- Docs-corpus validator warnings are pre-existing generated markdown header warnings outside this task output root.
