Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Project Graph Impact Model

Project graph impact queries are structured questions over graph facts. They return graph nodes, graph edges, confidence, diagnostics, evidence, and an optional incomplete reason. They are proof surfaces, not a query engine implementation.

Initial query kinds are:

- `what_depends_on`
- `what_does_this_command_use`
- `which_apps_expose`
- `which_tests_prove`
- `which_modules_display`
- `which_packs_provide`
- `which_release_artifacts_include`
- `which_public_surfaces_are_affected_by`
- `which_tasks_touched`

Confidence is `asserted`, `derived`, `observed`, or `inferred`. Asserted facts come directly from source truth. Derived facts come from deterministic extraction. Observed facts come from validation/audit/tool evidence. Inferred facts are weaker than asserted facts and must be presented with that limitation.

An incomplete query is acceptable when the result includes diagnostics and an incomplete reason. Missing graph results do not prove missing functionality, app exposure, test coverage, or release inclusion.
