#ifndef DOMINO_UI_RENDERER_H_INCLUDED
#define DOMINO_UI_RENDERER_H_INCLUDED

#include "domino/ui_layout.h"
#include "domino/ui_widget.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ui_renderer {
    int      width;
    int      height;
    int      dpi;
    int      viewports;
    ui_style theme;
} ui_renderer;

typedef struct ui_renderer_desc {
    int width;
    int height;
    int dpi;
    int viewports;
} ui_renderer_desc;

ui_renderer* ui_renderer_create(const ui_renderer_desc* desc);
void         ui_renderer_destroy(ui_renderer* r);
void         ui_renderer_set_theme(ui_renderer* r, const ui_style* theme);
void         ui_renderer_draw(ui_renderer* r, ui_node* root);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_UI_RENDERER_H_INCLUDED */
