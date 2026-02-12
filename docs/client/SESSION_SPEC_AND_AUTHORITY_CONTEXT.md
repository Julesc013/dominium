Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# SessionSpec And AuthorityContext

## Runtime Binding
- Client selection flow resolves:
  - `experience_id`
  - `scenario_id`
  - `mission_id`
  - `parameter_bundle_id`
- The resolved selection materializes a `SessionSpec` before launch.

## AuthorityContext
- `AuthorityContext` binds:
  - `authority_origin`
  - `experience_id`
  - `law_profile_id`
  - resolved entitlements/capability hash
  - epistemic scope + watermark policy
- Intents without authority context are refused.

## Enforcement Surfaces
- Client command bridge carries `authority_context_id` in session/status output.
- Server authority checks include context-aware validation for authoritative sessions.
- RepoX/TestX enforce schema presence and marker coverage.
