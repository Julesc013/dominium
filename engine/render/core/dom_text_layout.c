#include "dom_text_layout.h"

#include <string.h>

dom_err_t dom_text_layout_measure(const char *text,
                                  dom_i32 *out_width,
                                  dom_i32 *out_height)
{
    size_t len;
    if (!text || !out_width || !out_height) {
        return DOM_ERR_INVALID_ARG;
    }

    /* Simple deterministic placeholder: 8px per glyph, 8px tall. */
    len = strlen(text);
    *out_width = (dom_i32)(len * 8u);
    *out_height = 8;
    return DOM_OK;
}
