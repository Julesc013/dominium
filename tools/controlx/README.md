Status: CANONICAL
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# ControlX

ControlX is the autonomous control plane wrapper for queued prompt execution.
Prompts are treated as untrusted input and routed through the prompt firewall.

## Commands

- `python tools/controlx/controlx.py sanitize --prompt-file <path>`
- `python tools/controlx/controlx.py run --prompt-file <path> --repo-root .`
- `python tools/controlx/controlx.py run-queue --queue-file <path> --repo-root .`

## Control Contract

- Prompt text is parsed and sanitized before execution.
- Raw gate/tool invocations inside prompts are removed.
- Execution is routed through `scripts/dev/gate.py` (`precheck` then `exitcheck`).
- Mechanical failures trigger remediation flow and queue continuation.
- Semantic ambiguity is emitted in strict escalation template format.

## Audit Artifacts

ControlX writes deterministic run logs under `docs/audit/controlx/` by default:

- `SANITIZATION.md`
- `RUNLOG.json`
- `remediation_links.json`
- `<queue_id>.QUEUE_RUNLOG.json`
