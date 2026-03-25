Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored governance diagram after XStack and architecture freeze

# Repository Governance Diagram

## Governance Diagram

```text
AGENTS.md / task catalog / prompt surfaces / agent_context.json
                |
                v
             XStack
 RepoX / AuditX / TestX / ControlX / CompatX / SessionX
                |
                v
      architecture graph / module registry / dependency graph
                |
                v
 contracts / registries / schemas / baselines / proofs
                |
                v
        repository structure and runtime evidence
```

## Notes

- Prompts are untrusted inputs.
- XStack governance is authoritative.
- Architecture drift, duplicate semantic engines, and module boundary violations should be caught before merge.

