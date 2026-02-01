Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Recovery and Safe Mode

Doc Version: 1

Recovery is a deterministic, auditable policy layer that helps users return to a known-good state without silently changing simulation-affecting content.

## Launch History

Each instance maintains `logs/launch_history.tlv`, containing recent launch attempts:
- timestamp
- manifest hash and resolved config hash
- safe mode flag
- outcome classification (success/crash/refusal/missing artifacts)
- exit code and optional detail string

This history drives recovery suggestions.

## Auto-Recovery Suggestions

Based on a configured threshold (default 3), the launcher can:
- suggest safe mode after consecutive failures
- suggest rollback to last known-good snapshot
- optionally auto-enter safe mode for the next attempt (still audited)

## Safe Mode Overlay

Safe mode is a non-persistent overlay applied during prelaunch planning:
- disables mods/packs by default
- forces conservative graphics settings
- disables network by default

Safe mode is never written back unless explicitly confirmed.

## Known-Good Snapshots

After a successful launch, the launcher can record last-known-good:
- writes `known_good.tlv` as a pointer
- captures a snapshot under `previous/` containing the manifest and payload references needed to reproduce the known-good state

Rollback restores this snapshot through the transaction engine.

## Crash / Interrupted-Write Recovery

On startup (or before operations), the launcher performs best-effort staging recovery:
- reads transaction markers for audit context
- deletes staged artifacts
- preserves live state

All recovery actions are audited.

See `docs/launcher/INSTANCE_MODEL.md` and `docs/launcher/DIAGNOSTICS_AND_SUPPORT.md`.