# Secret / Local-State Scan

Status: needs_review

Command:

`rg -n "sk-[A-Za-z0-9]|sk-ant|api[_-]?key|SECRET|TOKEN|PASSWORD|BEGIN PRIVATE KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|DEEPSEEK_API_KEY" .aide .aide.local.example AGENTS.md README.md ROADMAP.md PLANS.md IMPLEMENT.md DOCUMENTATION.md docs canon specs data contracts tools scripts validation repo governance control cmake .gitignore`

Result: PASS after review.

The scan returned policy, detector, fixture, and test-rule strings such as `TOKEN`, `SECRET`, and `api_key` pattern text. No live provider credential, private key block, `.aide.local/` content, raw prompt dump, or raw response dump was identified.

Raw scan logs:

- `.aide/queue/DCHECK-01-dominium-aide-operating-baseline-audit/evidence/secret-scan-current.log`
- `.aide/queue/DCHECK-01-dominium-aide-operating-baseline-audit/evidence/secret-scan-final.log`

Final scan rerun after report generation returned matches only in policy, detector, fixture, generated map, and test-rule text. No live credential was identified.
