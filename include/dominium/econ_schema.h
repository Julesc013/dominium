/*
FILE: include/dominium/econ_schema.h
MODULE: Dominium
PURPOSE: Economy pack schema constants shared across tools and runtime.
*/
#ifndef DOMINIUM_ECON_SCHEMA_H
#define DOMINIUM_ECON_SCHEMA_H

#include "domino/core/types.h"

/* Record type IDs (u32, stable within econ packs). */
enum {
    ECON_REC_PACK_META        = 0x00000001u,
    ECON_REC_ASSET            = 0x00100001u,
    ECON_REC_MONEY_STANDARD   = 0x00100002u,
    ECON_REC_CONTRACT_TEMPLATE= 0x00100003u,
    ECON_REC_INSTRUMENT       = 0x00100004u
};

/* Record schema version (implicit in pack, recorded in manifest). */
enum { ECON_REC_VERSION_V1 = 1u };

/* Pack meta payload tags. */
enum {
    ECON_META_TAG_PACK_SCHEMA_VERSION = 1u,
    ECON_META_TAG_PACK_ID             = 2u,
    ECON_META_TAG_PACK_VERSION_NUM    = 3u,
    ECON_META_TAG_PACK_VERSION_STR    = 4u,
    ECON_META_TAG_CONTENT_HASH        = 5u
};

/* ASSET payload tags. */
enum {
    ECON_ASSET_TAG_ID                = 1u,
    ECON_ASSET_TAG_ID_HASH           = 2u,
    ECON_ASSET_TAG_KIND              = 3u,
    ECON_ASSET_TAG_UNIT_SCALE        = 4u,
    ECON_ASSET_TAG_DIVISIBILITY      = 5u,
    ECON_ASSET_TAG_PROVENANCE_REQ    = 6u,
    ECON_ASSET_TAG_DISPLAY_NAME      = 7u,
    ECON_ASSET_TAG_ISSUER_ID         = 8u,
    ECON_ASSET_TAG_ISSUER_ID_HASH    = 9u
};

/* MONEY_STANDARD payload tags. */
enum {
    ECON_MONEY_TAG_ID                = 1u,
    ECON_MONEY_TAG_ID_HASH           = 2u,
    ECON_MONEY_TAG_BASE_ASSET_ID     = 3u,
    ECON_MONEY_TAG_BASE_ASSET_HASH   = 4u,
    ECON_MONEY_TAG_DENOM_SCALE       = 5u,
    ECON_MONEY_TAG_ROUNDING_MODE     = 6u,
    ECON_MONEY_TAG_DISPLAY_NAME      = 7u,
    ECON_MONEY_TAG_CONVERT_RULE_ID   = 8u,
    ECON_MONEY_TAG_CONVERT_RULE_HASH = 9u
};

/* CONTRACT_TEMPLATE payload tags. */
enum {
    ECON_CONTRACT_TAG_ID             = 1u,
    ECON_CONTRACT_TAG_ID_HASH        = 2u,
    ECON_CONTRACT_TAG_OBLIGATION     = 3u
};

/* CONTRACT_OBLIGATION payload tags (nested in ECON_CONTRACT_TAG_OBLIGATION). */
enum {
    ECON_OBL_TAG_ROLE_FROM_ID        = 1u,
    ECON_OBL_TAG_ROLE_FROM_HASH      = 2u,
    ECON_OBL_TAG_ROLE_TO_ID          = 3u,
    ECON_OBL_TAG_ROLE_TO_HASH        = 4u,
    ECON_OBL_TAG_ASSET_ID            = 5u,
    ECON_OBL_TAG_ASSET_HASH          = 6u,
    ECON_OBL_TAG_AMOUNT_I64          = 7u,
    ECON_OBL_TAG_OFFSET_TICKS        = 8u
};

/* INSTRUMENT payload tags. */
enum {
    ECON_INSTRUMENT_TAG_ID           = 1u,
    ECON_INSTRUMENT_TAG_ID_HASH      = 2u,
    ECON_INSTRUMENT_TAG_KIND         = 3u,
    ECON_INSTRUMENT_TAG_CONTRACT_ID  = 4u,
    ECON_INSTRUMENT_TAG_CONTRACT_HASH= 5u,
    ECON_INSTRUMENT_TAG_ASSET_ID     = 6u,
    ECON_INSTRUMENT_TAG_ASSET_HASH   = 7u
};

/* Enums (stable). */
enum {
    ECON_ASSET_KIND_FUNGIBLE     = 1u,
    ECON_ASSET_KIND_NONFUNGIBLE  = 2u
};

enum {
    ECON_MONEY_ROUND_TRUNCATE    = 1u,
    ECON_MONEY_ROUND_FLOOR       = 2u,
    ECON_MONEY_ROUND_CEIL        = 3u,
    ECON_MONEY_ROUND_NEAREST_AWAY= 4u
};

enum {
    ECON_INSTRUMENT_LOAN         = 1u,
    ECON_INSTRUMENT_BOND         = 2u,
    ECON_INSTRUMENT_EQUITY       = 3u,
    ECON_INSTRUMENT_LEASE        = 4u,
    ECON_INSTRUMENT_OPTION       = 5u,
    ECON_INSTRUMENT_FUTURE       = 6u,
    ECON_INSTRUMENT_INSURANCE    = 7u
};

#endif /* DOMINIUM_ECON_SCHEMA_H */
