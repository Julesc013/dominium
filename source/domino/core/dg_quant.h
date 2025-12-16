/*
FILE: source/domino/core/dg_quant.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dg_quant
RESPONSIBILITY: Implements `dg_quant`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic quantization helpers (C89).
 *
 * Quantization is mandatory for all placement/edit intents before they become
 * authoritative state (BUILD / TRANS / STRUCT / DECOR).
 *
 * Engine rule:
 * - Unquantized placement commands are invalid.
 * - UI snapping is optional/external; the engine never assumes a grid.
 *
 * Canonical rounding:
 * - Quantization rounds to nearest multiple; halves are rounded away from zero.
 */
#ifndef DG_QUANT_H
#define DG_QUANT_H

#include "core/dg_pose.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Default quanta (Q48.16).
 * - Position: 1/1024 meter  => 65536 / 1024 = 64
 * - Angle:    1/4096 turn   => 65536 / 4096 = 16
 * - Param:    1/1024 unit   => 64 (unit depends on param space)
 */
#define DG_QUANT_POS_DEFAULT_Q   ((dg_q)64)
#define DG_QUANT_ANGLE_DEFAULT_Q ((dg_q)16)
#define DG_QUANT_PARAM_DEFAULT_Q ((dg_q)64)

/* Quantize scalar fixed-point values to a caller-provided quantum.
 * quantum_q MUST be > 0 (Q48.16). If quantum_q <= 0, the input is returned.
 */
dg_q dg_quant_pos(dg_q value_q, dg_q quantum_q);
dg_q dg_quant_angle(dg_q value_q, dg_q quantum_q);
dg_q dg_quant_param(dg_q value_q, dg_q quantum_q);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_QUANT_H */

