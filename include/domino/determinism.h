#ifndef DOMINO_DETERMINISM_H_INCLUDED
#define DOMINO_DETERMINISM_H_INCLUDED
/*
 * Determinism grades (C89/C++98 visible).
 *
 * These grades classify the determinism guarantee of a runtime subsystem or
 * backend implementation. They are used by the capability registry to select
 * backends deterministically and to enforce lockstep requirements.
 *
 * Rules (enforced by selection, not by convention):
 * - Lockstep/rollback authoritative simulation requires D0 for all
 *   lockstep-relevant subsystems.
 * - Selection MUST NOT silently downgrade determinism for a lockstep-relevant
 *   subsystem. It must select an eligible D0 alternative or fail explicitly.
 * - D2 (best-effort) subsystems may exist only when they cannot influence
 *   authoritative simulation decisions (presentation-only, tooling-only, etc.).
 */

#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_det_grade {
    /* Bit-exact across supported platforms: hashes/replays must match exactly. */
    DOM_DET_D0_BIT_EXACT = 0,

    /* Tick-exact semantics, but not guaranteed bit-identical (non-authoritative). */
    DOM_DET_D1_TICK_EXACT = 1,

    /* Best-effort / may vary across machines; must not affect authoritative state. */
    DOM_DET_D2_BEST_EFFORT = 2
} dom_det_grade;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_DETERMINISM_H_INCLUDED */

