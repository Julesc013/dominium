# Quality And Limitations

Compact packet quality:

- Contains objective, why, context refs, allowed paths, forbidden paths,
  implementation rules, validation commands, evidence requirements, acceptance,
  output schema, non-goals, and token estimate.
- Includes direct Dominium doctrine refs through
  `.aide/context/dominium-doctrine-refs.md` and canon/planning/reality paths.
- Does not include full file, full repo, full chat, or full doctrine dumps.

Validation quality:

- AIDE doctor: PASS
- AIDE validate: PASS
- AIDE verifier: WARN, no errors
- AIDE review packet: generated, PASS budget
- AIDE eval run: PASS, 6/6 golden tasks
- AIDE selftest/test: PASS
- Advisory route/cache/ledger reports: generated without provider/model/network
  calls

Limitations:

- Verifier WARN remains because cache metadata, the Q23 evidence queue path, and
  pre-existing dirty FAST validation report files are outside the active AIDE
  verifier task's default allowed-path inference.
- AIDE Lite uses chars/4 estimates, not exact tokenizer or billing data.
- Repo snapshot and repo map are metadata-only but large because Dominium is a
  large doctrine-heavy repository.
- Quality evidence is local and deterministic; no GPT review, LLM-as-judge, or
  provider review ran.
- Gateway/provider surfaces remain report-only metadata and no-call.
- Dominium product FAST validation was not rerun during Q23 to avoid overwriting
  pre-existing dirty validation artifacts.
- The selftest fix is target-local imported-script hardening; it does not import
  or activate live `core/gateway/**` or `core/providers/**` runtime code.

Q23 review should check:

- The imported `.aide/` contains no source AIDE queue/history/memory/generated
  context.
- The compact task packet carries enough doctrine refs for the next task.
- `.aide/context/ignore.yaml` properly balances generated-bloat pruning with
  audit report reference safety.
- `.aide/scripts/aide_lite.py` target-local doctrine-ref adaptation is acceptable
  as a Dominium import adjustment.

Before broad trust in Dominium:

- Add Dominium-specific golden tasks.
- Add task-class mappings for doctrine-heavy protected areas.
- Add curated context ref bundles for schema, pack, runtime, release, and domain
  work classes.
