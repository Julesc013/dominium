# Q33 Doctrine Preservation

## Discovered Doctrine References

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `docs/planning/POST_PI_EXECUTION_PLAN.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
- `specs/reality/**`
- `data/reality/**`

## Baseline

`.aide/context/dominium-doctrine-refs.md` already references doctrine by path
and explicitly avoids restating full doctrine. `.aide/memory/project-state.md`
is compact and also instructs future agents not to inline whole doctrine files.

## Final Result

- `.aide/memory/project-state.md` remained unchanged and compact:
  3,620 chars, about 905 tokens.
- `.aide/memory/decisions.md` and `.aide/memory/open-risks.md` remained
  unchanged.
- `.aide/context/dominium-doctrine-refs.md` remained unchanged.
- No files under `docs/canon/**`, `docs/planning/**`, `specs/**`, or `data/**`
  were modified.
- The latest task packet references doctrine by path and does not inline whole
  doctrine files.
- `AGENTS.md` manual doctrine and governance content was preserved; only the
  managed AIDE adapter block changed.

## Remaining Doctrine Risks

- Q33 does not prove complete doctrine coverage for future product tasks.
- Future tasks still need task-specific doctrine refs from
  `.aide/context/dominium-doctrine-refs.md`.
- Dominium-specific golden tasks may need refinement beyond the portable AIDE
  golden set.
