Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# STATUS_SR4

- SR-4 adds deterministic planning: resolve set + install_plan.tlv output with stable digests.
- Kernel produces plan, resolved set digest, and plan digest in setup_audit.tlv.
- CLI adds `plan`, `resolve`, and `dump-plan` commands with deterministic JSON output.
- No execution, transactions, or resumability work yet; legacy setup behavior remains unchanged.