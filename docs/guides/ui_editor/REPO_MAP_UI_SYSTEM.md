Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UI System Repo Map (current)

## Files and roles
- source/dominium/launcher/ui_schema/launcher_ui_v1.tlv — Launcher UI schema TLV used at runtime. Target: dominium-launcher (runtime load).
- scripts/gen_launcher_ui_schema_v1.py — Generator for launcher_ui_v1.tlv. Target: none (script).
- source/dominium/launcher/dom_launcher_app.cpp — Launcher app and UI wiring (schema discovery/loading). Target: dominium-launcher.
- source/dominium/launcher/dom_launcher_actions.cpp — Launcher UI actions/state transitions. Target: dominium-launcher.
- source/dominium/launcher/dom_launcher_catalog.cpp — Launcher catalog/model data for UI. Target: dominium-launcher.
- include/dui/dui_api_v1.h — DUI backend API v1 ABI. Target: domino_core (header used by DUI).
- include/dui/dui_schema_tlv.h — TLV tags/enums for DUI schema/state. Target: domino_core (header used by DUI).
- source/domino/dui/dui_schema_parse.h — DUI TLV schema/state parser interface. Target: domino_core.
- source/domino/dui/dui_schema_parse.c — DUI TLV schema/state parser/layout helpers. Target: domino_core.
- source/domino/dui/dui_event_queue.h — DUI event queue interface. Target: domino_core.
- source/domino/dui/dui_event_queue.c — DUI event queue implementation. Target: domino_core.
- source/domino/dui/dui_win32.c — Win32 DUI backend (native controls). Target: domino_core (WIN32-only source).
- source/domino/dui/dui_dgfx.c — DGFX DUI backend (software renderer). Target: domino_core.
- source/domino/dui/dui_null.c — Null/headless DUI backend. Target: domino_core.
- include/domino/io/container.h — DTLV reader/writer API used by DUI TLV parsing. Target: domino_core (header).
- source/domino/io/container/dtlv.c — DTLV reader/writer implementation. Target: domino_core.

## CMake ownership
- source/dominium/launcher/CMakeLists.txt defines dominium-launcher (includes dom_launcher_*.cpp; links domino_core + dominium_launcher_core).
- source/domino/CMakeLists.txt defines domino_core and compiles DUI backends and TLV container (dui_*.c, io/container/dtlv.c).

## Current UI pipeline (launcher)
- TLV schema/state (launcher_ui_v1.tlv) → DUI schema/state parser (dui_schema_parse) → DUI runtime → backend selection (win32 / dgfx / null).