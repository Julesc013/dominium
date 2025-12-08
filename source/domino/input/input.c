#include "domino/input.h"

#include <stdlib.h>
#include <string.h>

struct dom_input {
    uint32_t binding_count;
};

dom_status dom_input_create(dsys_context* sys, dom_input** out_input)
{
    dom_input* input;

    (void)sys;
    if (!out_input) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    *out_input = NULL;

    input = (dom_input*)malloc(sizeof(dom_input));
    if (!input) {
        return DOM_STATUS_ERROR;
    }
    memset(input, 0, sizeof(*input));

    *out_input = input;
    return DOM_STATUS_OK;
}

void dom_input_destroy(dom_input* input)
{
    if (!input) {
        return;
    }
    free(input);
}

dom_status dom_input_bind(dom_input* input, const dom_input_binding* binding)
{
    (void)binding;
    if (!input) {
        return DOM_STATUS_INVALID_ARGUMENT;
    }
    input->binding_count += 1u;
    return DOM_STATUS_OK;
}

dom_status dom_input_poll(dom_input* input, dom_input_sample* samples, uint32_t sample_capacity, uint32_t* out_sample_count)
{
    (void)input;
    (void)samples;
    (void)sample_capacity;
    if (out_sample_count) {
        *out_sample_count = 0u;
    }
    return DOM_STATUS_OK;
}
