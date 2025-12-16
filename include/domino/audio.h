/*
FILE: include/domino/audio.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / audio
RESPONSIBILITY: Defines the public contract for `audio` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_AUDIO_H_INCLUDED
#define DOMINO_AUDIO_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/* daudio_context: Public type used by `audio`. */
typedef struct daudio_context daudio_context;
/* daudio_buffer: Public type used by `audio`. */
typedef struct daudio_buffer    daudio_buffer;
/* daudio_voice_id: Public type used by `audio`. */
typedef uint32_t daudio_voice_id;

/* daudio_caps: Public type used by `audio`. */
typedef struct daudio_caps {
    const char* name;
    uint32_t    max_channels;
    bool        supports_streams;
    bool        supports_3d;
} daudio_caps;

/* daudio_desc: Public type used by `audio`. */
typedef struct daudio_desc {
    uint32_t sample_rate;
    uint32_t channels;
    uint32_t buffer_frames;
} daudio_desc;

/* Purpose: Init daudio.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
daudio_context* daudio_init(const daudio_desc* desc);
/* Purpose: Shutdown daudio.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            daudio_shutdown(daudio_context* ctx);
/* Purpose: Caps daudio get.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
daudio_caps     daudio_get_caps(daudio_context* ctx);

/* Purpose: Create buffer.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
daudio_buffer*  daudio_buffer_create(daudio_context* ctx,
                                     const float* interleaved_samples,
                                     uint32_t frame_count,
                                     uint32_t channel_count);
/* Purpose: Destroy buffer.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            daudio_buffer_destroy(daudio_context* ctx, daudio_buffer* buffer);

/* Purpose: Play daudio.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
daudio_voice_id daudio_play(daudio_context* ctx, const daudio_buffer* buffer, int loop);
/* Purpose: Stop daudio.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            daudio_stop(daudio_context* ctx, daudio_voice_id voice);
/* Purpose: Gain daudio set.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            daudio_set_gain(daudio_context* ctx, daudio_voice_id voice, float gain);
/* Purpose: Pan daudio set.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void            daudio_set_pan(daudio_context* ctx, daudio_voice_id voice, float pan);
/* Purpose: Stream daudio play.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
daudio_voice_id daudio_play_stream(daudio_context* ctx);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_AUDIO_H_INCLUDED */
