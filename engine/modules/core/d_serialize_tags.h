/*
FILE: source/domino/core/d_serialize_tags.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/d_serialize_tags
RESPONSIBILITY: Defines internal contract for `d_serialize_tags`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Subsystem TLV tags used in save/load containers. */
#ifndef D_SERIALIZE_TAGS_H
#define D_SERIALIZE_TAGS_H

enum {
    TAG_SUBSYS_DWORLD  = 0x1000,
    TAG_SUBSYS_DRES    = 0x1001,
    TAG_SUBSYS_DENV    = 0x1002,
    TAG_SUBSYS_DBULD   = 0x1003,
    TAG_SUBSYS_DTRANS  = 0x1004,
    TAG_SUBSYS_DSTRUCT = 0x1005,
    TAG_SUBSYS_DVEH    = 0x1006,
    TAG_SUBSYS_DJOB    = 0x1007,
    TAG_SUBSYS_DNET    = 0x1008,
    TAG_SUBSYS_DREPLAY = 0x1009,
    TAG_SUBSYS_DHYDRO  = 0x100A,
    TAG_SUBSYS_DLITHO  = 0x100B,
    TAG_SUBSYS_DORG    = 0x100C,
    TAG_SUBSYS_DRESEARCH = 0x100D,
    TAG_SUBSYS_DECON   = 0x100E,
    TAG_SUBSYS_DPOLICY = 0x100F
    /* Reserve 0x2000+ for mod/third-party subsystems */
};

#endif /* D_SERIALIZE_TAGS_H */
