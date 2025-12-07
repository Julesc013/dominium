#ifndef DOMINIUM_DOM_REND_H
#define DOMINIUM_DOM_REND_H

/* Renderer abstraction used by the game. Launcher/tools must not include this. */

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_REND_API_VERSION 1u

typedef struct dom_rend_device dom_rend_device;

struct dom_rend_desc {
    int width;
    int height;
    int fullscreen;
};

struct dom_rend_vtable {
    uint32_t api_version;

    dom_rend_device* (*create_device)(const struct dom_rend_desc*);
    void             (*destroy_device)(dom_rend_device*);

    void (*begin_frame)(dom_rend_device*);
    void (*end_frame)(dom_rend_device*);

    void (*clear)(dom_rend_device*, uint32_t rgba);
    void (*draw_rect)(dom_rend_device*, int x, int y, int w, int h, uint32_t rgba);
};

/* Choose best available renderer (software baseline). */
const struct dom_rend_vtable* dom_rend_choose_best(void);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_DOM_REND_H */
