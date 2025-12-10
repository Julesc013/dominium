#include "domino/gui/style.h"

static const dgui_style g_default_style = {
    { 16, 16, 24, 255 },   /* bg */
    { 28, 28, 40, 255 },   /* panel */
    { 64, 160, 255, 255 }, /* accent */
    { 220, 220, 235, 255 },/* text */
    2,                     /* padding */
    1                      /* spacing */
};

const dgui_style* dgui_style_default(void) {
    return &g_default_style;
}
