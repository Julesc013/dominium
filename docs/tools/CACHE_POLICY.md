Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Cache Policy

Status: canonical.
Scope: tool-generated derived data only.
Authority: canonical. Tools and packs MUST follow this.

## Binding rules
- All derived data MUST be written under `build/cache/assets/`.
- Derived data MUST be disposable and regenerable.
- Pack directories MUST remain source-only and immutable to tools.
- Cache deletion MUST NOT affect saves or packs.