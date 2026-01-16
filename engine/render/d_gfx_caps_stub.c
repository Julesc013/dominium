/*
FILE: source/domino/render/d_gfx_caps_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/d_gfx_caps_stub
RESPONSIBILITY: Provides a minimal DGFX capability stub for builds without render backends.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic constant values.
VERSIONING / ABI / DATA FORMAT NOTES: Internal stub; not part of public ABI.
EXTENSION POINTS: Replace with backend-capable implementation when render stack is wired.
*/
#include "d_gfx_caps.h"

u32 d_gfx_get_opcode_mask(void)
{
    return 0u;
}

u32 d_gfx_get_opcode_mask_for_backend(const char* name)
{
    (void)name;
    return 0u;
}

const char* d_gfx_get_backend_name(void)
{
    return "null";
}
