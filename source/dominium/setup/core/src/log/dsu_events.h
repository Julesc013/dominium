/*
FILE: source/dominium/setup/core/src/log/dsu_events.h
MODULE: Dominium Setup
PURPOSE: Shared event id constants for audit log emission.
*/
#ifndef DSU_EVENTS_H_INCLUDED
#define DSU_EVENTS_H_INCLUDED

#define DSU_EVENT_MANIFEST_LOADED 0x1001u
#define DSU_EVENT_RESOLVE_COMPLETE 0x1101u
#define DSU_EVENT_PLAN_BUILT 0x1201u
#define DSU_EVENT_PLAN_WRITTEN 0x1202u
#define DSU_EVENT_PLAN_LOADED 0x1203u
#define DSU_EVENT_DRY_RUN_START 0x1301u
#define DSU_EVENT_DRY_RUN_STEP 0x1302u
#define DSU_EVENT_DRY_RUN_COMPLETE 0x1303u
#define DSU_EVENT_AUDIT_LOG_WRITTEN 0x1401u

#endif /* DSU_EVENTS_H_INCLUDED */
