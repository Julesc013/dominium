Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# AIDE Changelog Preview

This reference summarizes the portable AIDE changelog preview workflow. The
canonical policy and templates live under `.aide/changelog/` and
`.aide/policies/changelog.yaml`.

Changelog previews are deterministic local evidence. They may be generated for
review, but they do not publish releases, create tags, upload assets, or mutate
remote repository state.

Commit messages remain the primary structured input for changelog extraction.
