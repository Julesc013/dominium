<!-- AIDE-GENERATED:BEGIN section=aide-token-survival-adapter target=codex_agents_md generator=aide-adapter-compiler-v0 version=q24.existing-tool-adapter-compiler.v0 source_template=.aide/adapters/templates/AGENTS.md.template mode=managed_section manual=outside-only fingerprint=sha256:8f573bef168a6f16af88c7aef03c771d113a5971324cafb15f8b8bed4374c597 -->
## AIDE Existing-Tool Adapter: Codex

- Use `.aide/context/latest-task-packet.md` as the default task brief.
- Use `.aide/context/latest-context-packet.md` for compact repo refs when the
  task packet points there.
- Do not paste long chat history, full repo dumps, raw prompts, raw responses,
  secrets, provider keys, or `.aide.local/` contents.
- Prefer exact repo refs and line refs over copied file bodies.
- Before substantive work, run `py -3 .aide/scripts/aide_lite.py doctor`,
  `validate`, and `pack --task "<bounded task>"` when available.
- For quality-sensitive work, run `verify`, `review-pack`, `eval run`, and
  evidence checks before review or promotion.
- For Q27-and-later work, use structured commits and run `commit check` when
  practical.
- Inspect `task status` or `task inspect` before repeated, partial, or
  out-of-order queue work.
- Run `git plan` before branch-sensitive work; do not mutate branches without
  an explicit helper plan, validation evidence, and operator approval.
- Treat Gateway and provider surfaces as no-call/report-only unless a future
  reviewed queue phase explicitly enables live execution.
- Write evidence, preserve manual content, stop at review gates, and report
  validation honestly.
<!-- AIDE-GENERATED:END section=aide-token-survival-adapter -->
