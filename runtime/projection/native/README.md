Status: DEFERRED
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Stability: provisional

# Native Projection

This directory reserves the runtime native projection mode boundary.

Native projection code must stay presentation-only and must not mutate
authoritative truth directly. Platform-specific provider glue belongs under the
owning `runtime/platform` or provider path.
