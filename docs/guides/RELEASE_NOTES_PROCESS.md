Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Release Notes + Tagging Process (Local, Offline)

This project treats `scripts\build_codex_verify.bat` as the single “done gate”.
Release notes are generated offline from commit subjects and then curated.

## 1) Preconditions

- Working tree is clean (`git status --porcelain`).
- Commits follow the conventions in `CONTRIBUTING.md` (prompt prefix +
  What/Why/Impact/Verification). The former `docs/COMMIT_CONVENTIONS.md` path is
  deprecated and no longer authoritative.
- Builds run with no downloads (`DOM_DISALLOW_DOWNLOADS=ON`).

## 2) Verify (“done gate”)

Run the canonical verification script:

```
scripts\build_codex_verify.bat
```

Expected outcome:

- prints per-config PASS/FAIL
- returns exit code `0` on success

See `docs/ci/BUILD_MATRIX.md` and `docs/specs/SPEC_SMOKE_TESTS.md` for the matrix entries
and smoke contract.

## 3) Generate a draft changelog (offline)

Generate a readable draft changelog grouped by prompt prefix and subsystem:

```
scripts\gen_changelog.bat
```

Optional ranges:

```
scripts\gen_changelog.bat --since <rev>
scripts\gen_changelog.bat --range <a..b>
```

Output:

- `docs/CHANGELOG_DRAFT.md` (generated; ignored by default via `docs/.gitignore`)

## 4) Curate into the authoritative changelog (optional)

Promote curated entries into:

- `CHANGELOG.md`

`docs/CHANGELOG_DRAFT.md` is intended to be disposable output; if you want to
commit it anyway, use:

```
git add -f docs/CHANGELOG_DRAFT.md
```

## 5) Tag a release (optional)

If you use tags, the generator defaults to “since last tag”.

Example (annotated tag):

```
git tag -a vX.Y.Z -m "vX.Y.Z"
git push --tags
```

## Related specs

- `docs/specs/SPEC_LANGUAGE_BASELINES.md`
- `docs/specs/SPEC_ABI_TEMPLATES.md`
- `docs/specs/SPEC_CAPABILITY_REGISTRY.md`
- `docs/specs/SPEC_LAUNCHER_PROFILES.md`
- `docs/specs/SPEC_CONTAINER_TLV.md`
- `docs/specs/SPEC_NET_HANDSHAKE.md`
- `docs/specs/SPEC_SMOKE_TESTS.md`