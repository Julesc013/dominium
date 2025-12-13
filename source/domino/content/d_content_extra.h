/* Shared TLV parameter tags for data-driven content (C89). */
#ifndef D_CONTENT_EXTRA_H
#define D_CONTENT_EXTRA_H

#include "domino/core/types.h"

/* Resource model params: generic solid strata */
#define D_TLV_RES_STRATA_MEAN_GRADE       0x01u
#define D_TLV_RES_STRATA_MEAN_QUANTITY    0x02u
#define D_TLV_RES_STRATA_NOISE_SCALE      0x03u
#define D_TLV_RES_STRATA_REGEN_RATE       0x04u

/* Generic process parameter tags */
#define D_TLV_PROCESS_RATE_PER_TICK       0x01u
#define D_TLV_PROCESS_DEPOSIT_VALUE_SLOT  0x02u
#define D_TLV_PROCESS_DEPLETION_AMOUNT    0x03u
#define D_TLV_PROCESS_OUTPUT_ITEM_ID      0x04u
#define D_TLV_PROCESS_OUTPUT_PER_TICK     0x05u

/* Structure layout tags */
#define D_TLV_STRUCT_LAYOUT_FOOTPRINT_W   0x01u
#define D_TLV_STRUCT_LAYOUT_FOOTPRINT_H   0x02u
#define D_TLV_STRUCT_LAYOUT_ANCHOR_Z      0x03u

/* Structure IO/ports */
#define D_TLV_STRUCT_IO_PORT              0x10u
#define D_TLV_STRUCT_PORT_KIND            0x01u
#define D_TLV_STRUCT_PORT_POS_X           0x02u
#define D_TLV_STRUCT_PORT_POS_Y           0x03u
#define D_TLV_STRUCT_PORT_DIR_Z           0x04u

enum {
    D_STRUCT_PORT_RESOURCE_IN = 1,
    D_STRUCT_PORT_ITEM_OUT    = 2,
    D_STRUCT_PORT_ITEM_IN     = 3
};

/* Structure process list */
#define D_TLV_STRUCT_PROCESS_ALLOWED      0x20u

/* Blueprint payload */
#define D_TLV_BLUEPRINT_STRUCTURE_PROTO   0x01u

#endif /* D_CONTENT_EXTRA_H */
