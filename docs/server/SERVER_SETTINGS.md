Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Server Settings

Server settings are authority-side runtime policy settings.

## NOW (implemented)

- `tick_rate`
- `authority_mode`
- `logging_level`
- `snapshot_interval`
- `srz_policy`

## SOON (scaffolded)

- advanced rate limits
- anti-cheat tuning knobs

## LATER (deferred)

- live policy dashboards

## Rules

- Client UI must not edit server settings directly.
- Server settings are set by server CLI/config and validated on load.
