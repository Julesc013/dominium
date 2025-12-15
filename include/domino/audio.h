#ifndef DOMINO_AUDIO_H_INCLUDED
#define DOMINO_AUDIO_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct daudio_context daudio_context;
typedef struct daudio_buffer    daudio_buffer;
typedef uint32_t daudio_voice_id;

typedef struct daudio_caps {
    const char* name;
    uint32_t    max_channels;
    bool        supports_streams;
    bool        supports_3d;
} daudio_caps;

typedef struct daudio_desc {
    uint32_t sample_rate;
    uint32_t channels;
    uint32_t buffer_frames;
} daudio_desc;

daudio_context* daudio_init(const daudio_desc* desc);
void            daudio_shutdown(daudio_context* ctx);
daudio_caps     daudio_get_caps(daudio_context* ctx);

daudio_buffer*  daudio_buffer_create(daudio_context* ctx,
                                     const float* interleaved_samples,
                                     uint32_t frame_count,
                                     uint32_t channel_count);
void            daudio_buffer_destroy(daudio_context* ctx, daudio_buffer* buffer);

daudio_voice_id daudio_play(daudio_context* ctx, const daudio_buffer* buffer, int loop);
void            daudio_stop(daudio_context* ctx, daudio_voice_id voice);
void            daudio_set_gain(daudio_context* ctx, daudio_voice_id voice, float gain);
void            daudio_set_pan(daudio_context* ctx, daudio_voice_id voice, float pan);
daudio_voice_id daudio_play_stream(daudio_context* ctx);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_AUDIO_H_INCLUDED */
