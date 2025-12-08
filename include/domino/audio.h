#ifndef DOMINO_AUDIO_H_INCLUDED
#define DOMINO_AUDIO_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct daudio_device daudio_device;

typedef struct daudio_device_desc {
    uint32_t      struct_size;
    uint32_t      struct_version;
    dsys_context* sys;
    uint32_t      sample_rate;
    uint32_t      channel_count;
    uint32_t      buffer_frames;
} daudio_device_desc;

typedef struct daudio_buffer {
    uint32_t struct_size;
    uint32_t struct_version;
    float*   interleaved_samples;
    uint32_t frame_count;
    uint32_t channel_count;
} daudio_buffer;

dom_status daudio_create_device(const daudio_device_desc* desc, daudio_device** out_device);
void       daudio_destroy_device(daudio_device* device);
dom_status daudio_submit_buffer(daudio_device* device, const daudio_buffer* buffer);
dom_status daudio_get_latency_ms(daudio_device* device, uint32_t* out_latency_ms);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_AUDIO_H_INCLUDED */
