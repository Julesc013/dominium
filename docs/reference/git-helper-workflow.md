Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# AIDE Git Helper Workflow

This reference summarizes portable Git helper behavior. The canonical policy is
`.aide/git/helper-policy.yaml`, with command notes in
`.aide/git/helper-commands.md`.

Git helper commands produce plans by default. Applying a plan requires explicit
flags, clean evidence, branch containment checks where relevant, and review
approval. Helpers must not force-push or delete protected branches.
