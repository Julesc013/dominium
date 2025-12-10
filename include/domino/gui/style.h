#ifndef DOMINO_GUI_STYLE_H_INCLUDED
#define DOMINO_GUI_STYLE_H_INCLUDED

#include "domino/render/gui_prim.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dgui_style {
    dgui_color bg;
    dgui_color panel;
    dgui_color accent;
    dgui_color text;
    int        padding;
    int        spacing;
} dgui_style;

const dgui_style* dgui_style_default(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_GUI_STYLE_H_INCLUDED */
