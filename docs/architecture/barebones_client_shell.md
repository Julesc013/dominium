Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: BAREBONES-CLIENT-SHELL-01

# Barebones Client Shell

The barebones client shell is the client product survival floor. It proves the client can report help, version, status, diagnostics, and verification without requiring optional packs, modules, themes, textures, sounds, external fonts, GPU rendering, networking, package runtime, provider runtime, module loading, gameplay, or world/save runtime.

This slice adds narrow command/result/refusal surfaces for:

- `dominium.client.status.v1`
- `dominium.client.diag.v1`
- `dominium.client.verify.v1`

The result schema is `contracts/result/client_barebones_result.schema.json`. It records available CLI/headless capabilities, explicit unavailable capabilities, optional content absence, diagnostics, refusal refs, limitations, and support-claim flags. The support-claim flags stay false for playable gameplay, rendered shell, package runtime, provider runtime, module loader, world runtime, and release support.

The client executable path is intentionally small:

- `client --help`
- `client --version`
- `client --status`
- `client --diag`
- `client --verify`

`--status`, `--diag`, and `--verify` print a deterministic text floor that names the product, available capabilities, expected missing optional content, and explicit unavailability refusals. This is not a broad AppShell, renderer, gameplay, package, provider, or module runtime.

## Explicit Refusals

The barebones client surfaces refuse unsupported capabilities by stable semantic IDs:

- `dominium.refusal.client.rendered_unavailable`
- `dominium.refusal.client.gameplay_unavailable`
- `dominium.refusal.client.world_runtime_unavailable`
- `dominium.refusal.client.package_runtime_unavailable`
- `dominium.refusal.client.provider_runtime_unavailable`
- `dominium.refusal.client.module_loader_unavailable`
- `dominium.refusal.client.mode_unsupported`

These refusals keep unsupported features visible rather than hidden behind fallback behavior.

## Non-Goals

This slice does not implement playable client behavior, rendered UI, renderer backends, native GUI, package runtime, provider runtime, runtime module loading, world/save runtime, release publication, or broad AppShell behavior.

## Next Work

The next review should decide whether the runtime/product spine is ready for broader presentation contracts, package/replay follow-up, or a minimal Workbench/product shell slice.
