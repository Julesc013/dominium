# Reader Brief — Dominium Language, Platform, and Architecture Baseline

## What this chat was about

This chat decided Dominium’s modern language/platform architecture. The key outcome is C17 + C++17, 64-bit, little-endian, C-compatible ABI, deterministic fixed-width data, and provider/capability modularity.

## Top 20 things to know

1. C17 + C++17 is the mainline direction.
2. C89/C++98 is superseded for mainline, preserved only for retro/projection/archive thinking.
3. Pure C99 was rejected as too weak for Dominium-scale modularity.
4. Pure C++11 was rejected as unnecessarily conservative.
5. C17 owns stable law and ABI-adjacent substrate.
6. C++17 owns machinery, providers, apps, Workbench, and tools.
7. Public boundaries remain C-compatible, POD-only, versioned, and no-exception.
8. No STL/classes/templates/RTTI/exceptions cross stable ABI.
9. Full source-native builds should be 64-bit: x86_64/arm64.
10. 32-bit is constrained/projection/archive only.
11. Little-endian mainline is accepted.
12. Save/replay/network/renderer IR cannot use pointer-sized/native-layout fields.
13. Raylib and SDL2 are providers, not identity.
14. Workbench is not authority; it must use commands/services/results/refusals/evidence.
15. Apps compose modules; modules require services; services use providers.
16. Packs provide data/modules/content.
17. Lockfiles and a composition resolver are missing central pieces.
18. Compatibility corpus and trust/permission model are missing.
19. Foundation Lock is currently blocked by dependency-direction strict failures.
20. The next action is dependency-direction repair, not product feature work.

## Best next step

Run and repair `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01`, then rerun Foundation Closeout.
