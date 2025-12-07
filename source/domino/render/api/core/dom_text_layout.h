#ifndef DOM_TEXT_LAYOUT_H
#define DOM_TEXT_LAYOUT_H

#include "dom_draw_common.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Deterministic placeholder text metrics used by vector-only paths. */
dom_err_t dom_text_layout_measure(const char *text,
                                  dom_i32 *out_width,
                                  dom_i32 *out_height);

#ifdef __cplusplus
}
#endif

#endif /* DOM_TEXT_LAYOUT_H */
