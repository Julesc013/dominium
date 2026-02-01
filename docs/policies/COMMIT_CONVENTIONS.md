Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Commit Conventions

This repository uses commit messages as the source of truth for:

- release notes (`scripts\gen_changelog.bat`)
- auditability (why a change exists, what it affects, how it was verified)
- prompt-by-prompt traceability (p1 … pN)

These rules are intentionally lightweight and repo-local (no hooks required).

## 1) Subject line (required)

Format:

```
pN: <summary>
```

Where:

- `pN` is the prompt identifier (`p1` … `p9`, and continuing for later prompts).
- `<summary>` is imperative, concise, and scoped (aim for ≤ 72 chars).

### 1.1 Optional subsystem tag (strongly recommended)

To make changelog grouping deterministic, put one subsystem keyword immediately
after the prompt prefix:

```
pN: docs: <summary>
pN: sys:  <summary>
pN: gfx:  <summary>
pN: io:   <summary>
pN: net:  <summary>
```

Notes:

- Use **one** primary subsystem per commit when possible.
- If a change is truly cross-cutting, omit the subsystem tag and the generator
  will place it under `misc`.

## 2) Body sections (required for non-trivial changes)

Body sections use fixed headings so tools (and humans) can skim reliably:

```
What:
- <what changed>

Why:
- <why it changed>

Impact:
- <runtime / ABI / determinism / tooling / docs impact>

Verification:
- <commands run and expected results>
```

Guidance:

- Keep bullets short and concrete.
- Put any compatibility statements in **Impact** (ABI, formats, determinism).
- Include the “done gate” when relevant:
  - `scripts\build_codex_verify.bat`

## 3) “No semantic change intended” (required when applicable)

If a commit is intentionally non-behavioral (formatting, comments, renames,
refactors intended to be semantics-preserving), include an explicit statement in
**Impact**:

```
Impact:
- No semantic change intended.
```

Also include:

- what was changed (e.g., “whitespace only”, “error text only”, “logging only”)
- what was **not** changed (APIs, formats, backend behavior)
- verification that supports the claim (tests/build/verify)

## 4) Small changes vs. exceptions

### 4.1 Docs-only or tooling-only commits

Docs/scripts changes still use the same structure, but can keep the body short.

### 4.2 Trivial commits

If the change is truly trivial (e.g., one-line typo fix), the body may be
omitted; otherwise, include the full body sections.

## 5) Examples

Subject with subsystem tag:

```
p9: docs: document release notes process and changelog generation
```

Semantics-preserving refactor:

```
p9: sys: tighten verify script failure reporting

What:
- Print per-step commands and stop on first failure.

Why:
- Make CI/local failures actionable without scrolling.

Impact:
- No semantic change intended (scripts only).

Verification:
- scripts\build_codex_verify.bat
```