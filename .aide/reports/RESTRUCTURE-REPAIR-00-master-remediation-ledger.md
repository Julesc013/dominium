# RESTRUCTURE-REPAIR-00 Master Remediation Ledger

Generated: 2026-05-17T16:08:43Z
Total issues: 54

Final repair result: PARTIAL.

Safe repairs were applied for stale app/client/runtime paths, archive contract paths, RepoX archive allowlist drift, TestX path-hygiene fixtures, ops JSON warning leakage, targeted doc contract references, and deterministic `slice0_hardcoded_ids` diagnostic output.

Remaining blockers are deferred rather than fixed here: 23 excepted former bad roots, full CTest failures/incompletion, frozen contract hash drift, expired override policy entries, replay hash mismatches, AuditX timeout cases, and the tracked large file-quality ledger policy warning.

| ID | Class | Severity | Safe Now | Status | Paths |
| --- | --- | --- | --- | --- | --- |
| RR00-0001 | root_remaining | blocker | false | deferred | `core/` |
| RR00-0002 | root_exception_remaining | warning | false | deferred | `core/` |
| RR00-0003 | root_remaining | blocker | false | deferred | `control/` |
| RR00-0004 | root_exception_remaining | warning | false | deferred | `control/` |
| RR00-0005 | root_remaining | blocker | false | deferred | `data/` |
| RR00-0006 | root_exception_remaining | warning | false | deferred | `data/` |
| RR00-0007 | root_remaining | blocker | false | deferred | `packs/` |
| RR00-0008 | root_exception_remaining | warning | false | deferred | `packs/` |
| RR00-0009 | root_remaining | blocker | false | deferred | `profiles/` |
| RR00-0010 | root_exception_remaining | warning | false | deferred | `profiles/` |
| RR00-0011 | root_remaining | blocker | false | deferred | `bundles/` |
| RR00-0012 | root_exception_remaining | warning | false | deferred | `bundles/` |
| RR00-0013 | root_remaining | blocker | false | deferred | `compat/` |
| RR00-0014 | root_exception_remaining | warning | false | deferred | `compat/` |
| RR00-0015 | root_remaining | blocker | false | deferred | `lib/` |
| RR00-0016 | root_exception_remaining | warning | false | deferred | `lib/` |
| RR00-0017 | root_remaining | blocker | false | deferred | `libs/` |
| RR00-0018 | root_exception_remaining | warning | false | deferred | `libs/` |
| RR00-0019 | root_remaining | blocker | false | deferred | `locks/` |
| RR00-0020 | root_exception_remaining | warning | false | deferred | `locks/` |
| RR00-0021 | root_remaining | blocker | false | deferred | `repo/` |
| RR00-0022 | root_exception_remaining | warning | false | deferred | `repo/` |
| RR00-0023 | root_remaining | blocker | false | deferred | `safety/` |
| RR00-0024 | root_exception_remaining | warning | false | deferred | `safety/` |
| RR00-0025 | root_remaining | blocker | false | deferred | `security/` |
| RR00-0026 | root_exception_remaining | warning | false | deferred | `security/` |
| RR00-0027 | root_remaining | blocker | false | deferred | `specs/` |
| RR00-0028 | root_exception_remaining | warning | false | deferred | `specs/` |
| RR00-0029 | root_remaining | blocker | false | deferred | `updates/` |
| RR00-0030 | root_exception_remaining | warning | false | deferred | `updates/` |
| RR00-0031 | root_remaining | blocker | false | deferred | `meta/` |
| RR00-0032 | root_exception_remaining | warning | false | deferred | `meta/` |
| RR00-0033 | root_remaining | blocker | false | deferred | `governance/` |
| RR00-0034 | root_exception_remaining | warning | false | deferred | `governance/` |
| RR00-0035 | root_remaining | blocker | false | deferred | `performance/` |
| RR00-0036 | root_exception_remaining | warning | false | deferred | `performance/` |
| RR00-0037 | root_remaining | blocker | false | deferred | `validation/` |
| RR00-0038 | root_exception_remaining | warning | false | deferred | `validation/` |
| RR00-0039 | root_remaining | blocker | false | deferred | `modding/` |
| RR00-0040 | root_exception_remaining | warning | false | deferred | `modding/` |
| RR00-0041 | root_remaining | blocker | false | deferred | `models/` |
| RR00-0042 | root_exception_remaining | warning | false | deferred | `models/` |
| RR00-0043 | root_remaining | blocker | false | deferred | `templates/` |
| RR00-0044 | root_exception_remaining | warning | false | deferred | `templates/` |
| RR00-0045 | root_remaining | blocker | false | deferred | `net/` |
| RR00-0046 | root_exception_remaining | warning | false | deferred | `net/` |
| RR00-0047 | validator_failure | blocker | false | blocked | `POST-RESTRUCTURE-00` |
| RR00-0048 | validator_failure | blocker | false | blocked | `DOE-00` |
| RR00-0049 | commit_policy_warning | blocker | false | pending | `.aide/reports/file-quality-ledger.json` |
| RR00-0050 | untracked_generated_noise | informational | false | accepted_warning | `.dominium.local/` |
| RR00-0051 | untracked_generated_noise | informational | false | accepted_warning | `.aide.local/` |
| RR00-0052 | untracked_generated_noise | informational | false | accepted_warning | `build/` |
| RR00-0053 | untracked_generated_noise | informational | false | accepted_warning | `out/` |
| RR00-0054 | untracked_generated_noise | informational | false | accepted_warning | `dist/` |
