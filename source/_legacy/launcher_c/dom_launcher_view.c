// LEGACY: candidate for removal/refactor
#include "dom_launcher_view.h"

/* Minimal theme definition (all integer colors, opaque ARGB). */
typedef struct DomLauncherTheme {
    DomColor bg;
    DomColor chrome;
    DomColor tab_bar;
    DomColor tab_active;
    DomColor tab_inactive;
    DomColor tab_underline;
    DomColor content_bg;
    DomColor sidebar;
    DomColor sidebar_slot;
    DomColor sidebar_divider;
    DomColor hero;
    DomColor hero_underline;
    DomColor paragraph;
    DomColor footer;
    DomColor footer_button_border;
    DomColor footer_button_fill;
    DomColor footer_status_border;
    DomColor footer_status_fill;
    DomColor text;
} DomLauncherTheme;

static const DomLauncherTheme g_theme = {
    /* bg                */ 0xFF1E1E1E,
    /* chrome            */ 0xFF2B2B2B,
    /* tab_bar           */ 0xFF1E1E1E,
    /* tab_active        */ 0xFF3A3A3A,
    /* tab_inactive      */ 0xFF2A2A2A,
    /* tab_underline     */ 0xFF4AA3FF,
    /* content_bg        */ 0xFF181818,
    /* sidebar           */ 0xFF1C1C1C,
    /* sidebar_slot      */ 0xFF232323,
    /* sidebar_divider   */ 0xFF444444,
    /* hero              */ 0xFF202020,
    /* hero_underline    */ 0xFF4AA3FF,
    /* paragraph         */ 0xFF1F1F1F,
    /* footer            */ 0xFF101010,
    /* footer_button_border */ 0xFF505050,
    /* footer_button_fill   */ 0xFF2D2D2D,
    /* footer_status_border */ 0xFF505050,
    /* footer_status_fill   */ 0xFF2D2D2D,
    /* text                */ 0xFFE7E7E7,
};

/* Very small 5x7 bitmap font for ASCII uppercase + digits + few symbols. */
typedef struct DomMiniGlyph {
    char ch;
    dom_u8 rows[7];
} DomMiniGlyph;

static const DomMiniGlyph g_font[] = {
    {'A',{0x0E,0x11,0x11,0x1F,0x11,0x11,0x11}},
    {'B',{0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E}},
    {'C',{0x0E,0x11,0x10,0x10,0x10,0x11,0x0E}},
    {'D',{0x1C,0x12,0x11,0x11,0x11,0x12,0x1C}},
    {'E',{0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F}},
    {'F',{0x1F,0x10,0x10,0x1E,0x10,0x10,0x10}},
    {'G',{0x0E,0x11,0x10,0x17,0x11,0x11,0x0F}},
    {'H',{0x11,0x11,0x11,0x1F,0x11,0x11,0x11}},
    {'I',{0x0E,0x04,0x04,0x04,0x04,0x04,0x0E}},
    {'J',{0x07,0x02,0x02,0x02,0x12,0x12,0x0C}},
    {'K',{0x11,0x12,0x14,0x18,0x14,0x12,0x11}},
    {'L',{0x10,0x10,0x10,0x10,0x10,0x10,0x1F}},
    {'M',{0x11,0x1B,0x15,0x11,0x11,0x11,0x11}},
    {'N',{0x11,0x19,0x15,0x13,0x11,0x11,0x11}},
    {'O',{0x0E,0x11,0x11,0x11,0x11,0x11,0x0E}},
    {'P',{0x1E,0x11,0x11,0x1E,0x10,0x10,0x10}},
    {'Q',{0x0E,0x11,0x11,0x11,0x15,0x12,0x0D}},
    {'R',{0x1E,0x11,0x11,0x1E,0x14,0x12,0x11}},
    {'S',{0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E}},
    {'T',{0x1F,0x04,0x04,0x04,0x04,0x04,0x04}},
    {'U',{0x11,0x11,0x11,0x11,0x11,0x11,0x0E}},
    {'V',{0x11,0x11,0x11,0x11,0x11,0x0A,0x04}},
    {'W',{0x11,0x11,0x11,0x11,0x15,0x1B,0x11}},
    {'X',{0x11,0x11,0x0A,0x04,0x0A,0x11,0x11}},
    {'Y',{0x11,0x11,0x0A,0x04,0x04,0x04,0x04}},
    {'Z',{0x1F,0x01,0x02,0x04,0x08,0x10,0x1F}},
    {'0',{0x0E,0x11,0x13,0x15,0x19,0x11,0x0E}},
    {'1',{0x04,0x0C,0x14,0x04,0x04,0x04,0x1F}},
    {'2',{0x0E,0x11,0x01,0x0E,0x10,0x10,0x1F}},
    {'3',{0x1F,0x01,0x02,0x06,0x01,0x11,0x0E}},
    {'4',{0x02,0x06,0x0A,0x12,0x1F,0x02,0x02}},
    {'5',{0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E}},
    {'6',{0x06,0x08,0x10,0x1E,0x11,0x11,0x0E}},
    {'7',{0x1F,0x01,0x02,0x04,0x08,0x08,0x08}},
    {'8',{0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E}},
    {'9',{0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C}},
    {' ',{0x00,0x00,0x00,0x00,0x00,0x00,0x00}},
    {'/',{0x01,0x01,0x02,0x04,0x08,0x10,0x10}},
    {'-',{0x00,0x00,0x00,0x1F,0x00,0x00,0x00}},
};

static const DomMiniGlyph *dom_find_glyph(char ch)
{
    dom_u32 i;
    for (i = 0; i < (dom_u32)(sizeof(g_font)/sizeof(g_font[0])); ++i) {
        if (g_font[i].ch == ch) return &g_font[i];
    }
    return 0;
}

static void dom_draw_char(DomRenderer *r, dom_i32 x, dom_i32 y, char ch, DomColor color)
{
    const DomMiniGlyph *g = dom_find_glyph(ch);
    dom_i32 row, col;
    DomRect px;
    if (!r || !g) return;
    px.w = 2;
    px.h = 2;
    for (row = 0; row < 7; ++row) {
        dom_u8 bits = g->rows[row];
        for (col = 0; col < 5; ++col) {
            if (bits & (1u << (4 - col))) {
                px.x = x + col * 2;
                px.y = y + row * 2;
                dom_render_rect(r, &px, color);
            }
        }
    }
}

static void dom_draw_text(DomRenderer *r, dom_i32 x, dom_i32 y, const char *text, DomColor color)
{
    dom_i32 pen_x = x;
    if (!r || !text) return;
    while (*text) {
        char ch = *text++;
        if (ch == '\n') {
            y += 9;
            pen_x = x;
            continue;
        }
        dom_draw_char(r, pen_x, y, ch, color);
        pen_x += 8;
    }
}

static void dom_draw_tabs(DomRenderer *r, dom_i32 y, dom_i32 width)
{
    DomRect rect;
    dom_i32 tx = 8;
    dom_i32 ty = y;
    dom_i32 th = 28;
    dom_i32 tw = 120;
    dom_i32 i;
    const dom_i32 tab_gap = 8;

    rect.x = 0; rect.y = y - 28; rect.w = width; rect.h = 28;
    dom_render_rect(r, &rect, g_theme.tab_bar);

    for (i = 0; i < 5; ++i) {
        DomColor c = (i == 0) ? g_theme.tab_active : g_theme.tab_inactive;
        const char *label = "";
        switch (i) {
        case 0: label = "NEWS"; break;
        case 1: label = "CHANGES"; break;
        case 2: label = "MODS"; break;
        case 3: label = "INSTANCES"; break;
        case 4: label = "SETTINGS"; break;
        default: label = ""; break;
        }
        rect.x = tx + i * (tw + tab_gap);
        rect.y = ty;
        rect.w = tw;
        rect.h = th;
        dom_render_rect(r, &rect, c);
        if (i == 0) {
            DomRect u;
            u.x = rect.x;
            u.y = rect.y + th - 3;
            u.w = rect.w;
            u.h = 3;
            dom_render_rect(r, &u, g_theme.tab_underline);
        }
        dom_draw_text(r, rect.x + 8, rect.y + 8, label, g_theme.text);
    }
}

static void dom_draw_segment_bar(DomRenderer *r,
                                 dom_i32 x,
                                 dom_i32 y,
                                 dom_i32 w,
                                 dom_i32 h,
                                 dom_i32 segments,
                                 dom_i32 active_index)
{
    dom_i32 i;
    dom_i32 gap = 4;
    dom_i32 seg_w;
    DomRect rc;
    if (segments <= 0) return;
    seg_w = (w - (segments - 1) * gap) / segments;
    for (i = 0; i < segments; ++i) {
        rc.x = x + i * (seg_w + gap);
        rc.y = y;
        rc.w = seg_w;
        rc.h = h;
        dom_render_rect(r, &rc, (i == active_index) ? g_theme.footer_button_border : g_theme.footer_button_fill);
    }
}

void dom_launcher_draw(DomRenderer *r, dom_u32 w, dom_u32 h)
{
    DomRect rect;
    dom_u32 i;
    if (!r) return;

    /* Background */
    rect.x = 0; rect.y = 0; rect.w = (dom_i32)w; rect.h = (dom_i32)h;
    dom_render_rect(r, &rect, g_theme.bg);

    /* Top chrome bar */
    rect.x = 0; rect.y = 0; rect.w = (dom_i32)w; rect.h = 28;
    dom_render_rect(r, &rect, g_theme.chrome);

    /* Tabs: News, Changes, Mods, Instances, Settings (active: News) */
    dom_draw_tabs(r, 28, (dom_i32)w);

    /* Content area */
    rect.x = 0; rect.y = 56; rect.w = (dom_i32)w; rect.h = (dom_i32)(h - 128);
    dom_render_rect(r, &rect, g_theme.content_bg);

    /* Sidebar */
    rect.x = (dom_i32)(w - 240);
    rect.y = 64;
    rect.w = 224;
    rect.h = (dom_i32)(h - 144);
    dom_render_rect(r, &rect, g_theme.sidebar);

    /* Sidebar slots */
    {
        dom_i32 sx = rect.x + 12;
        dom_i32 sy = rect.y + 12;
        dom_i32 sw = rect.w - 24;
        dom_i32 sh = 26;
        for (i = 0; i < 8; ++i) {
            DomRect slot;
            DomRect underline;
            slot.x = sx;
            slot.y = sy + (dom_i32)i * (sh + 6);
            slot.w = sw;
            slot.h = sh;
            dom_render_rect(r, &slot, g_theme.sidebar_slot);
            underline.x = slot.x;
            underline.y = slot.y + sh - 2;
            underline.w = slot.w;
            underline.h = 2;
            dom_render_rect(r, &underline, g_theme.sidebar_divider);
            dom_draw_text(r, slot.x + 6, slot.y + 6, "ENTRY", g_theme.text);
        }
    }

    /* Main content block */
    rect.x = 12;
    rect.y = 64;
    rect.w = (dom_i32)(w - 264);
    rect.h = (dom_i32)(h - 144);
    dom_render_rect(r, &rect, g_theme.content_bg);
    dom_draw_text(r, rect.x + 16, rect.y + 16, "NEWS FEED / SESSION SUMMARY", g_theme.text);

    /* Hero block */
    {
        DomRect hero;
        DomRect underline;
        hero.x = rect.x + 12;
        hero.y = rect.y + 12;
        hero.w = rect.w - 24;
        hero.h = 80;
        dom_render_rect(r, &hero, g_theme.hero);
        underline.x = hero.x;
        underline.y = hero.y + hero.h - 4;
        underline.w = hero.w;
        underline.h = 4;
        dom_render_rect(r, &underline, g_theme.hero_underline);
        dom_draw_text(r, hero.x + 12, hero.y + 14, "LATEST BULLETIN", g_theme.text);
    }

    /* Paragraph placeholders */
    {
        dom_i32 px = rect.x + 12;
        dom_i32 py = rect.y + 108;
        dom_i32 pw = rect.w - 24;
        dom_i32 ph = 18;
        for (i = 0; i < 5; ++i) {
            DomRect line;
            line.x = px;
            line.y = py + (dom_i32)i * 26;
            line.w = pw;
            line.h = ph;
            dom_render_rect(r, &line, g_theme.paragraph);
        }
    }

    /* Footer */
    rect.x = 0; rect.y = (dom_i32)(h - 84); rect.w = (dom_i32)w; rect.h = 84;
    dom_render_rect(r, &rect, g_theme.footer);

    /* Footer: instance dropdown */
    {
        DomRect btn;
        dom_i32 y = (dom_i32)(h - 68);
        btn.x = 16; btn.y = y; btn.w = 160; btn.h = 32;
        dom_render_rect(r, &btn, g_theme.footer_button_border);
        btn.x += 2; btn.y += 2; btn.w -= 4; btn.h -= 4;
        dom_render_rect(r, &btn, g_theme.footer_button_fill);
        dom_draw_text(r, btn.x + 6, btn.y + 6, "INSTANCE A", g_theme.text);
    }

    /* Footer: exe bitness selector (8/16/32/64) */
    dom_draw_segment_bar(r, 190, (dom_i32)(h - 68), 220, 32, 4, 2);
    dom_draw_text(r, 190, (dom_i32)(h - 84), "BITNESS", g_theme.text);

    /* Footer: client/server selector */
    dom_draw_segment_bar(r, 420, (dom_i32)(h - 68), 160, 32, 2, 0);
    dom_draw_text(r, 420, (dom_i32)(h - 84), "ROLE", g_theme.text);

    /* Footer: graphical/headless selector */
    dom_draw_segment_bar(r, 590, (dom_i32)(h - 68), 200, 32, 2, 0);
    dom_draw_text(r, 590, (dom_i32)(h - 84), "MODE", g_theme.text);

    /* Play button */
    {
        DomRect play;
        play.x = (dom_i32)(w - 220);
        play.y = (dom_i32)(h - 72);
        play.w = 200;
        play.h = 48;
        dom_render_rect(r, &play, g_theme.footer_button_border);
        play.x += 2; play.y += 2; play.w -= 4; play.h -= 4;
        dom_render_rect(r, &play, g_theme.tab_underline);
        dom_draw_text(r, play.x + 60, play.y + 14, "PLAY", g_theme.text);
    }

    /* Footer session details panel */
    {
        DomRect status;
        status.w = 220;
        status.h = 48;
        status.x = (dom_i32)(w - status.w - 16);
        status.y = (dom_i32)(h - 124);
        dom_render_rect(r, &status, g_theme.footer_status_border);
        status.x += 2; status.y += 2; status.w -= 4; status.h -= 4;
        dom_render_rect(r, &status, g_theme.footer_status_fill);
        dom_draw_text(r, status.x + 8, status.y + 8, "SESSION DETAILS", g_theme.text);
    }
}
