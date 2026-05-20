# Root Risk Summary

- no_apply: true
- deletion_approval: false

## Risks

- `.aide`: risk=high status=mixed reasons=identity_sensitive_hint, build_sensitive_file_hint, authority_sensitive_hint, generated_sensitive_content
- `.aide.local.example`: risk=high status=review_required reasons=unknown_kind_or_owner
- `.github`: risk=high status=review_required reasons=unknown_kind_or_owner
- `.vscode`: risk=high status=review_required reasons=unknown_kind_or_owner
- `apps`: risk=high status=mixed reasons=build_sensitive_file_hint, unknown_kind_or_owner, multiple_file_kinds
- `archive`: risk=high status=review_required reasons=identity_sensitive_hint, build_sensitive_file_hint, generated_sensitive_content, unknown_kind_or_owner
- `cmake`: risk=high status=review_required reasons=build_sensitive_file_hint, unknown_kind_or_owner
- `content`: risk=high status=mixed reasons=build_sensitive_file_hint, unknown_kind_or_owner, multiple_file_kinds
- `contracts`: risk=high status=review_required reasons=identity_sensitive_hint, build_sensitive_file_hint, authority_sensitive_hint, unknown_kind_or_owner
- `docs`: risk=high status=mixed reasons=generated_sensitive_content, generated_source_mix, unknown_kind_or_owner, multiple_file_kinds
- `engine`: risk=high status=review_required reasons=build_sensitive_file_hint, unknown_kind_or_owner
- `game`: risk=high status=review_required reasons=build_sensitive_file_hint, unknown_kind_or_owner
- `release`: risk=high status=mixed reasons=identity_sensitive_hint, build_sensitive_file_hint, authority_sensitive_hint, generated_sensitive_content
- `repo-root`: risk=high status=mixed reasons=build_sensitive_file_hint, authority_sensitive_hint, generated_sensitive_content, generated_source_mix
- `runtime`: risk=high status=mixed reasons=build_sensitive_file_hint, unknown_kind_or_owner, multiple_file_kinds
- `scripts`: risk=high status=mixed reasons=build_sensitive_file_hint, generated_sensitive_content, generated_source_mix, unknown_kind_or_owner
- `tests`: risk=high status=mixed reasons=identity_sensitive_hint, build_sensitive_file_hint, authority_sensitive_hint, generated_sensitive_content
- `tools`: risk=high status=review_required reasons=build_sensitive_file_hint, unknown_kind_or_owner
