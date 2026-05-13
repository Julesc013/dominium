<!-- AIDE-GENERATED:BEGIN section=aide-token-survival-adapter target=continue generator=aide-adapter-compiler-v0 version=q24.existing-tool-adapter-compiler.v0 source_template=.aide/adapters/templates/continue-checks.template.md mode=preview_only manual=outside-only fingerprint=sha256:cd80049a968fbe6343eed04898073ba10576fabf02e79416ac6363846eb978d4 -->
# AIDE Token-Survival Check For Continue

Before handing work to an assistant:

- Prefer `.aide/context/latest-task-packet.md` over long chat history.
- Confirm the request does not require full-repo prompting.
- Keep secrets, provider keys, raw prompts, raw responses, and `.aide.local/`
  out of committed context.
- Run `py -3 .aide/scripts/aide_lite.py validate` and generate or refresh a
  compact packet with `pack --task "<bounded task>"` when useful.
- Use `verify` and `review-pack` for evidence-bearing changes.
- Treat Gateway/provider metadata as advisory; no live forwarding is enabled.
<!-- AIDE-GENERATED:END section=aide-token-survival-adapter -->
