/*
FILE: source/domino/launcher/ui_layout.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / launcher/ui_layout
RESPONSIBILITY: Implements `ui_layout`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>
#include "domino/ui_layout.h"

static void ui_layout_apply(ui_node* node)
{
    ui_node* child;
    int child_count;
    int flex_sum;
    int spacing;
    int available_w;
    int available_h;
    int cursor;

    if (!node) {
        return;
    }

    child = node->first_child;
    child_count = 0;
    flex_sum = 0;
    while (child) {
        child_count += 1;
        if (child->flex > 0) {
            flex_sum += child->flex;
        }
        child = child->next_sibling;
    }

    spacing = child_count > 1 ? node->gap * (child_count - 1) : 0;
    available_w = node->box.w - node->pad[0] - node->pad[2] - spacing;
    available_h = node->box.h - node->pad[1] - node->pad[3] - spacing;

    cursor = 0;
    child = node->first_child;
    while (child) {
        int cw;
        int ch;
        if (node->dir == UI_DIR_ROW) {
            if (flex_sum > 0 && child->flex > 0) {
                cw = (available_w * child->flex) / flex_sum;
            } else if (child_count > 0) {
                cw = available_w / child_count;
            } else {
                cw = available_w;
            }
            if (child->min_w > 0 && cw < child->min_w) {
                cw = child->min_w;
            }
            if (child->max_w > 0 && cw > child->max_w) {
                cw = child->max_w;
            }
            ch = available_h;
            if (child->min_h > 0 && ch < child->min_h) {
                ch = child->min_h;
            }
            if (child->max_h > 0 && ch > child->max_h) {
                ch = child->max_h;
            }
            child->box.x = node->box.x + node->pad[0] + cursor;
            child->box.y = node->box.y + node->pad[1];
            child->box.w = cw;
            child->box.h = ch;
            cursor += cw + node->gap;
        } else {
            if (flex_sum > 0 && child->flex > 0) {
                ch = (available_h * child->flex) / flex_sum;
            } else if (child_count > 0) {
                ch = available_h / child_count;
            } else {
                ch = available_h;
            }
            if (child->min_h > 0 && ch < child->min_h) {
                ch = child->min_h;
            }
            if (child->max_h > 0 && ch > child->max_h) {
                ch = child->max_h;
            }
            cw = available_w;
            if (child->min_w > 0 && cw < child->min_w) {
                cw = child->min_w;
            }
            if (child->max_w > 0 && cw > child->max_w) {
                cw = child->max_w;
            }
            child->box.x = node->box.x + node->pad[0];
            child->box.y = node->box.y + node->pad[1] + cursor;
            child->box.w = cw;
            child->box.h = ch;
            cursor += ch + node->gap;
        }
        ui_layout_apply(child);
        child = child->next_sibling;
    }
}

void ui_layout_compute(ui_layout_ctx* ctx, ui_node* root)
{
    if (!ctx || !root) {
        return;
    }
    root->box = ctx->viewport;
    ui_layout_apply(root);
}
