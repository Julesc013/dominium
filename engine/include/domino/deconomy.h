/*
FILE: include/domino/deconomy.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / deconomy
RESPONSIBILITY: Defines the public contract for `deconomy` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DECONOMY_H
#define DOMINO_DECONOMY_H

#include "dnumeric.h"
#include "dmatter.h"
#include "dorbit.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Market registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint32_t MarketId;
/* Purpose: Offer registry identifier. A value of 0 is treated as invalid by this API. */
typedef uint32_t OfferId;

/* Purpose: Offer direction for a market listing. */
typedef enum {
    OFFER_BUY = 0,
    OFFER_SELL,
} OfferType;

/* Purpose: Market definition record (POD).
 *
 * Ownership:
 * - `name` is a borrowed, NUL-terminated string; registry copies the pointer/record as implemented.
 */
typedef struct {
    MarketId    id;
    const char *name;
    BodyId      body;
} Market;

/* Purpose: Market offer/listing record (POD).
 *
 * Notes:
 *   - `price_per_unit` is Q16.16 fixed-point.
 */
typedef struct {
    OfferId     id;
    MarketId    market;
    OfferType   type;

    ItemTypeId  item;
    U32         quantity;
    Q16_16      price_per_unit;
} Offer;

/* Registers a market definition.
 *
 * Purpose: Add a market record to the economy registry.
 *
 * Parameters:
 *   - def: Input definition (must be non-NULL and `def->name` must be non-NULL).
 *         `*def` is copied into internal storage; caller retains ownership.
 *
 * Returns:
 *   - Non-zero MarketId on success; 0 on failure (invalid input or capacity limit).
 */
MarketId decon_market_register(const Market *def);

/* Looks up a market by id.
 *
 * Purpose: Retrieve a previously registered market record.
 *
 * Returns:
 *   - Pointer to internal storage on success; NULL if `id` is invalid.
 */
Market  *decon_market_get(MarketId id);

/* Registers an offer/listing.
 *
 * Purpose: Add an offer record to the economy registry.
 *
 * Parameters:
 *   - def: Input definition (must be non-NULL). `*def` is copied into internal storage.
 *
 * Returns:
 *   - Non-zero OfferId on success; 0 on failure (invalid input or capacity limit).
 */
OfferId  decon_offer_register(const Offer *def);

/* Looks up an offer by id.
 *
 * Purpose: Retrieve a previously registered offer record.
 *
 * Returns:
 *   - Pointer to internal storage on success; NULL if `id` is invalid.
 */
Offer   *decon_offer_get(OfferId id);

/* Finds the best active SELL offer for an item.
 *
 * Purpose: Search offers for the lowest-priced SELL entry with non-zero quantity.
 *
 * Returns:
 *   - OfferId of the lowest-priced SELL offer with non-zero quantity; 0 if none exist.
 */
OfferId  decon_find_best_sell_offer(ItemTypeId item);

/* Finds the best active BUY offer for an item.
 *
 * Purpose: Search offers for the highest-priced BUY entry with non-zero quantity.
 *
 * Returns:
 *   - OfferId of the highest-priced BUY offer with non-zero quantity; 0 if none exist.
 */
OfferId  decon_find_best_buy_offer(ItemTypeId item);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DECONOMY_H */
