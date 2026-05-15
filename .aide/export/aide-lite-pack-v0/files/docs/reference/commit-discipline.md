# AIDE Commit Discipline

This reference summarizes the portable AIDE commit discipline. The canonical
policy surfaces are `.aide/policies/commit-messages.yaml`,
`.aide/hooks/commit-msg`, and `.aide/reports/aide-commit-message-standard.md`.

Commits must use `type(scope): summary`, include the required Markdown
sections, record validation outcomes, include a machine-readable changelog
category, and carry the AIDE trailers required by the active policy.

This document is portable guidance only. It does not install hooks, mutate Git,
push branches, rewrite history, or override repository-specific review gates.
