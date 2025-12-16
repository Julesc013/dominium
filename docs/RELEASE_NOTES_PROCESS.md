# Release Notes + Tagging Process (Local, Offline)

This project treats `scripts\build_codex_verify.bat` as the single “done gate”.
Release notes are generated offline from commit subjects and then curated.

## 1) Preconditions

- Working tree is clean (`git status --porcelain`).
- Commits follow `docs/COMMIT_CONVENTIONS.md` (prompt prefix + What/Why/Impact/Verification).
- Builds run with no downloads (`DOM_DISALLOW_DOWNLOADS=ON`).

## 2) Verify (“done gate”)

Run the canonical verification script:

```
scripts\build_codex_verify.bat
```

Expected outcome:

- prints per-config PASS/FAIL
- returns exit code `0` on success

See `docs/BUILD_MATRIX.md` and `docs/SPEC_SMOKE_TESTS.md` for the matrix entries
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

- `docs/SPEC_LANGUAGE_BASELINES.md`
- `docs/SPEC_ABI_TEMPLATES.md`
- `docs/SPEC_CAPABILITY_REGISTRY.md`
- `docs/SPEC_LAUNCHER_PROFILES.md`
- `docs/SPEC_CONTAINER_TLV.md`
- `docs/SPEC_NET_HANDSHAKE.md`
- `docs/SPEC_SMOKE_TESTS.md`
