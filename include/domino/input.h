#ifndef DOMINO_INPUT_H_INCLUDED
#define DOMINO_INPUT_H_INCLUDED

#include <stdint.h>
#include "domino/core.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_input dom_input;

typedef struct dom_input_binding {
    uint32_t      struct_size;
    uint32_t      struct_version;
    uint32_t      action_id;
    uint32_t      key_code;
    float         scale;
} dom_input_binding;

typedef struct dom_input_sample {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t action_id;
    int      active;
    float    value;
} dom_input_sample;

dom_status dom_input_create(dsys_context* sys, dom_input** out_input);
void       dom_input_destroy(dom_input* input);
dom_status dom_input_bind(dom_input* input, const dom_input_binding* binding);
dom_status dom_input_poll(dom_input* input, dom_input_sample* samples, uint32_t sample_capacity, uint32_t* out_sample_count);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_INPUT_H_INCLUDED */
