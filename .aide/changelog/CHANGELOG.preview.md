# AIDE Changelog Preview

source_range: HEAD~20..HEAD
commit_count: 20
release_publishing: false

## Changed

- imported portable AIDE governance and recovery tooling into Dominium. (f2a1b4412cbe aide(dominium): sync portable commit and WorkUnit policies)
- added Dominium-local Git workflow reports and dry-run helper plan outputs. (4f04a866b73c aide(dominium): sync Git workflow policy and reports)

## Fixed

- prevented AIDE Lite selftest from resolving Dominium product `core` modules. (f2a1b4412cbe aide(dominium): sync portable commit and WorkUnit policies)

## Docs

- added compact Dominium AIDE governance sync reference. (4252584e060b docs(dominium): record canonical AIDE governance sync)

## Tests

- recorded 25/25 portable golden tasks passing after target-local helper-plan generation. (d722727e80e1 aide(dominium): regenerate packets and validation evidence)

## Internal

- added the Q33 queue and evidence recovery surface. (dd843482c92d aide(dominium): add canonical governance sync packet)
- refreshed Codex adapter guidance for governance-aware task recovery and branch planning. (4f04a866b73c aide(dominium): sync Git workflow policy and reports)
- refreshed Dominium-local AIDE generated reports and review evidence. (d722727e80e1 aide(dominium): regenerate packets and validation evidence)
- refreshed final Q33 generated validation artifacts. (752918d4f281 aide(dominium): refresh final validation artifacts)

## Malformed Commits

- 49ee68ca8f69 chore(repo): retire generated output root exceptions: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- e81e6d7f2a97 chore(repo): retire root wrapper and tooling exceptions: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- ed571cd32cd9 chore(repo): retire content and pack root exceptions: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 44bf83626fd1 chore(repo): narrow high-risk contract root exceptions: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- b08080e478c1 audit(repo): review core control and net ownership: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- b5d89feadad1 fix(repo): remediate post-converge build and gate blockers: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 4ccb80276ed4 audit(runtime): classify canonical local playtest blockers: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 9083d064bc37 audit(apps): classify product boot blockers: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 3455d6976847 audit(distribution): classify portable projection blockers: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 40b71c11a9ff audit(build): add tuple build contract and probe blockers: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 2aed29926182 audit(build): reprobe toolchains and classify native build blockers: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 4e256e81c37c fix(build): repair stale product source paths and classify next blocker: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 0f842071f543 fix(build): refresh UI bind generated outputs for native build: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
- 06d383b3d855 audit(test): classify AuditX CTest blockers after native build: commit body contains heading: ## Changelog; commit body heading has content: ## Changelog; commit body heading has bullet content: ## Changelog; validation section records PASS/WARN/FAIL/NOT RUN outcome; changelog section uses a machine-readable category prefix; commit trailer present: AIDE-Scope; commit trailer present: AIDE-Token-Impact
