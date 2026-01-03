# Documentation Standards

## Purpose
The documentation ratios are drift detectors. They flag when code becomes under-
documented or over-documented so changes stay reviewable and stable over time.

## Definitions
Counts only:
- C/C++ line comments using `//`
- C/C++ block comments using `/* ... */`

Does not count:
- generated code (by path exclusion)
- third-party or vendored code (by path exclusion)
- build outputs and external dependencies (by path exclusion)

## Exclusions
The default excluded path fragments are:
- `third_party`
- `external`
- `build`
- `out`
- `.git`
- `generated`

These are matched as path fragments anywhere in the normalized file path.

## Metrics
The quality gate computes ratios from aggregate totals across all scanned files:
- **Line ratio**: comment lines / total non-blank lines
- **Word ratio**: comment words / total words on non-blank lines
- **Character ratio**: comment characters / total characters on non-blank lines

Totals are summed first, then ratios are calculated from those sums (not an
average of per-file ratios). Strings and character literals are stripped before
comment extraction to avoid counting comment markers inside literals.

## Thresholds (Standard)
- Line ratio: min 0.20, max 0.40
- Word ratio: min 0.15, max 0.30
- Character ratio: min 0.10, max 0.25

## Local vs CI Behavior
- Local builds run in warn mode and do not fail the build.
- CI runs in fail mode when `CI` is set to a truthy value, exits non-zero, and
  blocks the build on threshold violations.

## Tuning
Configure via CMake cache variables:
- `DOC_RATIO_ENABLE`
- `DOC_RATIO_ROOTS`
- `DOC_RATIO_EXCLUDES`
- `DOC_RATIO_EXTS`
- `DOC_RATIO_MIN_LINE`, `DOC_RATIO_MAX_LINE`
- `DOC_RATIO_MIN_WORD`, `DOC_RATIO_MAX_WORD`
- `DOC_RATIO_MIN_CHAR`, `DOC_RATIO_MAX_CHAR`

## Script Limitations
The checker is heuristic:
- It strips string and character literals before parsing comments.
- It is not an AST parser and does not understand full C/C++ syntax.

## Maintenance Guidance
- Update roots and excludes when the repository layout changes.
- Keep ratios stable to detect drift instead of relaxing thresholds.
