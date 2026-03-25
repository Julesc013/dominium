Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored runtime architecture diagram after componentization planning

# Runtime Architecture Diagram

## Layered Diagram

```text
Applications
  client / server / setup / launcher / tools
        |
        v
Runtime Orchestrator
  lifecycle manager / scheduler / service registry / module loader
        |
        v
Services
  render / logic / storage / network / asset / save / observability / trust
        |
        v
Modules
  render backends / platform adapters / audio / input / storage / scripting
        |
        v
Engine Kernel
  assemblies / fields / processes / law / time / determinism
        |
        v
Game Layer
  dominium rules / content / baseline packs
```

## Reading Guide

- The engine kernel and game layer are the current strongest foundations.
- The runtime orchestrator and service layer are the main Φ-series targets.
- Applications must stay outside authoritative truth mutation except through lawful process execution.

