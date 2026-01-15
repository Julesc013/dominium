/*
FILE: source/domino/sim/replay/serialize/save_tlv.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/replay/serialize/save_tlv
RESPONSIBILITY: Defines internal contract for `save_tlv`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SAVE_TLV_H
#define DOM_SAVE_TLV_H

#include "core_types.h"
#include <stdio.h>

typedef struct ChunkSectionHeader {
    u32 type;
    u16 version;
    u16 reserved;
    u32 length;
} ChunkSectionHeader;

int tlv_read_header(FILE *f, ChunkSectionHeader *out);
int tlv_skip_section(FILE *f, const ChunkSectionHeader *hdr);
int tlv_write_section(FILE *f, u32 type, u16 version, const void *payload, u32 length);

#endif /* DOM_SAVE_TLV_H */
