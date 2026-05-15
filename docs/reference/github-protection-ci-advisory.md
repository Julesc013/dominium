# AIDE GitHub Protection And CI Advisory

This reference summarizes portable GitHub protection and CI advisory guidance.
The canonical policy surfaces are `.aide/policies/github-protection.yaml`,
`.aide/policies/ci-gates.yaml`, and `.aide/policies/branch-protection.yaml`.

The advisory is report-only. It does not call the GitHub API, mutate branch
protection, create workflow files, install CI, publish releases, create tags, or
upload assets.

Existing repository workflow files are outside the advisory mutation surface.
