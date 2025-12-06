#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef _WIN32_IE
#define _WIN32_IE 0x0501
#endif
#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#include <windows.h>
#include <commctrl.h>
#include <richedit.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>
#include <stdlib.h>

#include "dom_build_version.h"

/* Launcher version (launcher-specific). */
#define DOM_LAUNCHER_VERSION "0.0.0"

/* Control IDs */
#define IDC_TAB            1001
#define IDC_NEWS           1002
#define IDC_LINKS          1003
#define IDC_CONSOLE        1004
#define IDC_ACCOUNT_COMBO  1005
#define IDC_INSTANCE_COMBO 1006
#define IDC_PLATFORM_COMBO 1007
#define IDC_UI_COMBO       1008
#define IDC_RENDER_COMBO   1009
#define IDC_BTN_PLAY       1010
#define IDC_STATUS         1011
#define WM_APP_CONSOLE_APPEND (WM_APP + 1)

static HFONT g_ui_font = NULL;
static HINSTANCE g_hinst = NULL;
static HBRUSH g_br_bg = NULL;
static HBRUSH g_br_panel = NULL;
static HBRUSH g_br_bottom = NULL;
static HWND g_console_edit = NULL;
static HWND g_main_hwnd = NULL;

/* Colors */
typedef struct Theme {
    COLORREF bg;
    COLORREF panel;
    COLORREF bottom;
    COLORREF text;
    COLORREF link;
} Theme;

static Theme g_theme;

typedef struct LauncherStrings {
    const wchar_t *title;
    const wchar_t *tab_news;
    const wchar_t *tab_changes;
    const wchar_t *tab_mods;
    const wchar_t *tab_instances;
    const wchar_t *tab_settings;
    const wchar_t *tab_console;
    const char *news_utf8;
    const char *links_utf8;
    const wchar_t *status_ready;
    const wchar_t *btn_play;
} LauncherStrings;

typedef struct TabContent {
    const char *body_utf8;
    const char *links_utf8;
} TabContent;

static const LauncherStrings g_strings = {
    L"Dominium Launcher",
    L"News",
    L"Changes",
    L"Mods",
    L"Instances",
    L"Settings",
    L"Console",
    "Minecraft News\n\n"
    "Welcome to Dominium Launcher!\n"
    "Introducing the launcher, updated and ready. Current features include:\n\n"
    "\xE2\x80\xA2 UTF-8 aware UI using system fonts\n"
    "\xE2\x80\xA2 Native Win32 controls (tabs, buttons, combo)\n"
    "\xE2\x80\xA2 Scrollable news pane\n\n"
    "Planned features include:\n"
    "\xE2\x80\xA2 Profile management\n"
    "\xE2\x80\xA2 Instance selection\n"
    "\xE2\x80\xA2 Update checking\n\n"
    "We'll keep you posted.\n",
    "Official links:\n"
    "Dominium.net\n"
    "Forums\n"
    "Bug tracker\n"
    "Support\n"
    "Twitter\n"
    "Discord\n",
    L"Ready to update & play Dominium",
    L"Play",
};

static const TabContent g_tab_content[6] = {
    {   /* News */
        "Minecraft News\n\n"
        "Welcome to Dominium Launcher!\n"
        "Introducing the launcher, updated and ready. Current features include:\n\n"
        "\xE2\x80\xA2 UTF-8 aware UI using system fonts\n"
        "\xE2\x80\xA2 Native Win32 controls (tabs, buttons, combo)\n"
        "\xE2\x80\xA2 Scrollable news pane\n\n"
        "Planned features include:\n"
        "\xE2\x80\xA2 Profile management\n"
        "\xE2\x80\xA2 Instance selection\n"
        "\xE2\x80\xA2 Update checking\n\n"
        "We'll keep you posted.\n",
        "Official links:\n"
        "Dominium.net\n"
        "Forums\n"
        "Bug tracker\n"
        "Support\n"
        "Twitter\n"
        "Discord\n"
    },
    {   /* Changes */
        "Changes\n\n"
        "- Latest patches and release notes.\n"
        "- Display changelog here per build.\n",
        "Links:\n"
        "Release notes\n"
        "Issue tracker\n"
        "Commit history\n"
    },
    {   /* Mods */
        "Mods\n\n"
        "- Manage installed mods.\n"
        "- Browse, enable, disable.\n",
        "Links:\n"
        "Modding guide\n"
        "API docs\n"
    },
    {   /* Instances */
        "Instances\n\n"
        "- Configure instances/profiles.\n"
        "- Storage paths, saves, data packs.\n",
        "Links:\n"
        "Instance docs\n"
        "Backup guide\n"
    },
    {   /* Settings */
        "Settings\n\n"
        "- Adjust platform/backends.\n"
        "- UI mode, renderer, logging.\n",
        "Links:\n"
        "Preferences\n"
        "Support\n"
    },
    {   /* Console placeholder (body unused; console view shows live output) */
        "",
        ""
    }
};

static int utf8_to_wide(const char *utf8, wchar_t **out_wide)
{
    int wlen;
    wchar_t *buf;
    if (!utf8 || !out_wide) return 0;
    wlen = MultiByteToWideChar(CP_UTF8, 0, utf8, -1, NULL, 0);
    if (wlen <= 0) return 0;
    buf = (wchar_t *)malloc((size_t)wlen * sizeof(wchar_t));
    if (!buf) return 0;
    MultiByteToWideChar(CP_UTF8, 0, utf8, -1, buf, wlen);
    *out_wide = buf;
    return wlen;
}

static void set_font(HWND hwnd)
{
    if (g_ui_font) {
        SendMessage(hwnd, WM_SETFONT, (WPARAM)g_ui_font, TRUE);
    }
}

static void layout_controls(HWND hwnd, RECT client)
{
    const int tab_height = 28;
    const int padding = 8;
    const int right_panel_w = 200;
    const int bottom_h = 64;
    int content_top = tab_height + padding;
    int content_bottom = client.bottom - bottom_h - padding;
    int content_left = padding;
    int content_right = client.right - right_panel_w - 2 * padding;

    HWND htab = GetDlgItem(hwnd, IDC_TAB);
    HWND hnews = GetDlgItem(hwnd, IDC_NEWS);
    HWND hlinks = GetDlgItem(hwnd, IDC_LINKS);
    HWND haccount = GetDlgItem(hwnd, IDC_ACCOUNT_COMBO);
    HWND hinst = GetDlgItem(hwnd, IDC_INSTANCE_COMBO);
    HWND hplat = GetDlgItem(hwnd, IDC_PLATFORM_COMBO);
    HWND hui = GetDlgItem(hwnd, IDC_UI_COMBO);
    HWND hrend = GetDlgItem(hwnd, IDC_RENDER_COMBO);
    HWND hplay = GetDlgItem(hwnd, IDC_BTN_PLAY);
    HWND hstatus = GetDlgItem(hwnd, IDC_STATUS);

    MoveWindow(htab, 0, 0, client.right, tab_height + padding, TRUE);

    MoveWindow(hnews,
               content_left,
               content_top,
               content_right - content_left,
               content_bottom - content_top,
               TRUE);
    MoveWindow(hlinks,
               content_right + padding,
               content_top,
               right_panel_w,
               content_bottom - content_top,
               TRUE);
    if (g_console_edit) {
        MoveWindow(g_console_edit,
                   content_left,
                   content_top,
                   content_right - content_left + right_panel_w + padding,
                   content_bottom - content_top,
                   TRUE);
    }

    /* Bottom bar */
    {
        int y = client.bottom - bottom_h + padding;
        int x = padding;
        int w = 130;
        int gap = 8;
        MoveWindow(haccount, x, y, w, 24, TRUE); x += w + gap;
        MoveWindow(hinst, x, y, w, 24, TRUE);    x += w + gap;
        MoveWindow(hplat, x, y, w, 24, TRUE);    x += w + gap;
        MoveWindow(hui,   x, y, w, 24, TRUE);    x += w + gap;
        MoveWindow(hrend, x, y, w, 24, TRUE);    x += w + gap;

        /* Play button inline after dropdowns */
        MoveWindow(hplay, x, y, 120, 24, TRUE); x += 120 + gap;

        /* Status fills remaining space to the right */
        if (x < client.right - padding) {
            MoveWindow(hstatus, x, y, client.right - padding - x, 24, TRUE);
        }
    }
}

static void populate_news(HWND hnews)
{
    /* Default to News tab content */
    int tab = 0;
    wchar_t *wtext = NULL;
    if (!utf8_to_wide(g_tab_content[tab].body_utf8, &wtext)) return;
    SendMessageW(hnews, WM_SETTEXT, 0, (LPARAM)wtext);
    free(wtext);
}

static void populate_links(HWND hlinks)
{
    int tab = 0;
    wchar_t *wtext = NULL;
    if (!utf8_to_wide(g_tab_content[tab].links_utf8, &wtext)) return;
    SendMessageW(hlinks, WM_SETTEXT, 0, (LPARAM)wtext);
    free(wtext);
}

static void style_richedit(HWND h, COLORREF bg, COLORREF fg)
{
    SendMessageW(h, EM_SETBKGNDCOLOR, 0, bg);

    /* Set text color */
    {
        CHARFORMAT2W cf;
        memset(&cf, 0, sizeof(cf));
        cf.cbSize = sizeof(cf);
        cf.dwMask = CFM_COLOR | CFM_SIZE | CFM_FACE;
        cf.crTextColor = fg;
        cf.yHeight = 200; /* 10pt */
        lstrcpyW(cf.szFaceName, L"Segoe UI");
        SendMessageW(h, EM_SETCHARFORMAT, SCF_ALL, (LPARAM)&cf);
    }

    SendMessageW(h, EM_SETMARGINS, EC_LEFTMARGIN | EC_RIGHTMARGIN, MAKELPARAM(6, 6));
}

static void refresh_brushes(void)
{
    if (g_br_bg) DeleteObject(g_br_bg);
    if (g_br_panel) DeleteObject(g_br_panel);
    if (g_br_bottom) DeleteObject(g_br_bottom);
    g_br_bg = CreateSolidBrush(g_theme.bg);
    g_br_panel = CreateSolidBrush(g_theme.panel);
    g_br_bottom = CreateSolidBrush(g_theme.bottom);
}

static Theme make_theme_dark(void)
{
    Theme t;
    t.bg = RGB(26, 26, 26);
    t.panel = RGB(32, 32, 32);
    t.bottom = RGB(46, 46, 46);
    t.text = RGB(232, 232, 232);
    t.link = RGB(120, 170, 255);
    return t;
}

static Theme make_theme_light(void)
{
    Theme t;
    t.bg = GetSysColor(COLOR_WINDOW);
    t.panel = GetSysColor(COLOR_BTNFACE);
    t.bottom = GetSysColor(COLOR_BTNFACE);
    t.text = GetSysColor(COLOR_WINDOWTEXT);
    t.link = GetSysColor(COLOR_HOTLIGHT);
    return t;
}

static Theme make_theme_high_contrast(void)
{
    Theme t;
    t.bg = GetSysColor(COLOR_WINDOW);
    t.panel = GetSysColor(COLOR_WINDOW);
    t.bottom = GetSysColor(COLOR_BTNFACE);
    t.text = GetSysColor(COLOR_WINDOWTEXT);
    t.link = GetSysColor(COLOR_HOTLIGHT);
    return t;
}

static int is_color_light(COLORREF c)
{
    int r = GetRValue(c);
    int g = GetGValue(c);
    int b = GetBValue(c);
    int lum = (299 * r + 587 * g + 114 * b) / 1000;
    return lum > 128;
}

static void choose_theme(void)
{
    HIGHCONTRASTW hc;
    Theme t;
    memset(&hc, 0, sizeof(hc));
    hc.cbSize = sizeof(hc);
    if (SystemParametersInfoW(SPI_GETHIGHCONTRAST, sizeof(hc), &hc, 0) && (hc.dwFlags & HCF_HIGHCONTRASTON)) {
        t = make_theme_high_contrast();
    } else {
        COLORREF sys_win = GetSysColor(COLOR_WINDOW);
        if (is_color_light(sys_win)) {
            t = make_theme_light();
        } else {
            t = make_theme_dark();
        }
    }
    g_theme = t;
    refresh_brushes();
}

static void restyle_content(HWND hwnd)
{
    HWND hnews = GetDlgItem(hwnd, IDC_NEWS);
    HWND hlinks = GetDlgItem(hwnd, IDC_LINKS);
    if (hnews) style_richedit(hnews, g_theme.panel, g_theme.text);
    if (hlinks) style_richedit(hlinks, g_theme.panel, g_theme.link);
    if (g_console_edit) style_richedit(g_console_edit, g_theme.panel, g_theme.text);
    InvalidateRect(hwnd, NULL, TRUE);
}

static void set_content_for_tab(int tab_index, HWND hwnd)
{
    HWND hnews = GetDlgItem(hwnd, IDC_NEWS);
    HWND hlinks = GetDlgItem(hwnd, IDC_LINKS);
    HWND hconsole = g_console_edit;
    const TabContent *tc;
    wchar_t *wbody = NULL;
    wchar_t *wlinks = NULL;

    if (tab_index < 0 || tab_index >= 6) {
        tab_index = 0;
    }
    /* If console tab selected, show console, hide news/links */
    if (tab_index == 5) {
        if (hnews) ShowWindow(hnews, SW_HIDE);
        if (hlinks) ShowWindow(hlinks, SW_HIDE);
        if (hconsole) ShowWindow(hconsole, SW_SHOW);
        return;
    }

    tc = &g_tab_content[tab_index];

    if (hconsole) ShowWindow(hconsole, SW_HIDE);
    if (hnews) ShowWindow(hnews, SW_SHOW);
    if (hlinks) ShowWindow(hlinks, SW_SHOW);
    if (utf8_to_wide(tc->body_utf8, &wbody)) {
        SendMessageW(hnews, WM_SETTEXT, 0, (LPARAM)wbody);
        free(wbody);
    }
    if (utf8_to_wide(tc->links_utf8, &wlinks)) {
        SendMessageW(hlinks, WM_SETTEXT, 0, (LPARAM)wlinks);
        free(wlinks);
    }
}

static int get_combo_text(HWND combo, wchar_t *buf, int buf_count)
{
    LRESULT idx;
    if (!combo || !buf || buf_count <= 0) return 0;
    idx = SendMessageW(combo, CB_GETCURSEL, 0, 0);
    if (idx == CB_ERR) return 0;
    return (int)SendMessageW(combo, CB_GETLBTEXT, (WPARAM)idx, (LPARAM)buf);
}

static void set_status(HWND hwnd, const wchar_t *text)
{
    HWND hstatus = GetDlgItem(hwnd, IDC_STATUS);
    if (hstatus) {
        SendMessageW(hstatus, WM_SETTEXT, 0, (LPARAM)text);
    }
}

static DWORD WINAPI pipe_thread_fn(LPVOID param)
{
    HANDLE hPipe = (HANDLE)param;
    char buffer[512];
    DWORD read;
    while (ReadFile(hPipe, buffer, sizeof(buffer), &read, NULL) && read > 0) {
        int wlen = MultiByteToWideChar(CP_UTF8, 0, buffer, (int)read, NULL, 0);
        if (wlen <= 0) {
            wlen = MultiByteToWideChar(CP_ACP, 0, buffer, (int)read, NULL, 0);
        }
        if (wlen > 0) {
            wchar_t *wbuf = (wchar_t *)malloc((size_t)(wlen + 1) * sizeof(wchar_t));
            if (wbuf) {
                MultiByteToWideChar(CP_UTF8, 0, buffer, (int)read, wbuf, wlen);
                wbuf[wlen] = L'\0';
                if (g_main_hwnd) {
                    PostMessageW(g_main_hwnd, WM_APP_CONSOLE_APPEND, 0, (LPARAM)wbuf);
                } else {
                    free(wbuf);
                }
            }
        }
    }
    CloseHandle(hPipe);
    return 0;
}

static void launch_game_impl(HWND hwnd)
{
    wchar_t account[64] = L"";
    wchar_t instance[64] = L"";
    wchar_t platform[64] = L"";
    wchar_t ui_mode[64] = L"";
    wchar_t renderer[64] = L"";
    wchar_t exe_path[MAX_PATH];
    wchar_t workdir[MAX_PATH];
    wchar_t cmdline[512];
    HANDLE hRead = NULL, hWrite = NULL;
    SECURITY_ATTRIBUTES sa;
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    wchar_t *slash;
    int headless = 0;

    get_combo_text(GetDlgItem(hwnd, IDC_ACCOUNT_COMBO), account, 64);
    get_combo_text(GetDlgItem(hwnd, IDC_INSTANCE_COMBO), instance, 64);
    get_combo_text(GetDlgItem(hwnd, IDC_PLATFORM_COMBO), platform, 64);
    get_combo_text(GetDlgItem(hwnd, IDC_UI_COMBO), ui_mode, 64);
    get_combo_text(GetDlgItem(hwnd, IDC_RENDER_COMBO), renderer, 64);

    /* Headless/TUI modes skip game window; still hide console window regardless. */
    if (_wcsicmp(ui_mode, L"CLI") == 0 || _wcsicmp(ui_mode, L"TUI") == 0) {
        headless = 1;
    }

    /* Resolve executable path relative to launcher: ../client/dom_client.exe */
    if (GetModuleFileNameW(NULL, exe_path, MAX_PATH) == 0) {
        set_status(hwnd, L"Failed to resolve launcher path");
        return;
    }
    slash = wcsrchr(exe_path, L'\\');
    if (slash) {
        *slash = L'\0';
    }
    swprintf(workdir, MAX_PATH, L"%ls\\..\\client", exe_path);
    swprintf(exe_path, MAX_PATH, L"%ls\\dom_client.exe", workdir);

    swprintf(cmdline, 512, L"\"%ls\" --account=\"%ls\" --instance=\"%ls\" --platform=\"%ls\" --ui=\"%ls\" --renderer=\"%ls\"",
             exe_path,
             account[0] ? account : L"default",
             instance[0] ? instance : L"default",
             platform[0] ? platform : L"win32",
             ui_mode[0] ? ui_mode : L"gui",
             renderer[0] ? renderer : L"software");

    memset(&sa, 0, sizeof(sa));
    sa.nLength = sizeof(sa);
    sa.bInheritHandle = TRUE;
    if (!CreatePipe(&hRead, &hWrite, &sa, 0)) {
        set_status(hwnd, L"Failed to create pipe");
        return;
    }
    SetHandleInformation(hRead, HANDLE_FLAG_INHERIT, 0);

    memset(&si, 0, sizeof(si));
    memset(&pi, 0, sizeof(pi));
    si.cb = sizeof(si);
    si.dwFlags |= STARTF_USESTDHANDLES;
    si.hStdOutput = hWrite;
    si.hStdError = hWrite;
    si.hStdInput = GetStdHandle(STD_INPUT_HANDLE);

    set_status(hwnd, L"Launching...");
    if (!CreateProcessW(NULL, cmdline, NULL, NULL, TRUE, CREATE_NO_WINDOW | (headless ? CREATE_NO_WINDOW : 0), NULL, workdir, &si, &pi)) {
        wchar_t msg[128];
        swprintf(msg, 128, L"Launch failed (err=%lu)", GetLastError());
        set_status(hwnd, msg);
        CloseHandle(hRead);
        CloseHandle(hWrite);
        return;
    }
    CloseHandle(hWrite);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);

    /* Spawn reader thread to feed console tab */
    if (!CreateThread(NULL, 0, pipe_thread_fn, hRead, 0, NULL)) {
        CloseHandle(hRead);
    }

    set_status(hwnd, L"Game launched");
}
static LRESULT CALLBACK dom_launcher_wndproc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    switch (msg) {
    case WM_SIZE: {
        RECT rc;
        GetClientRect(hwnd, &rc);
        layout_controls(hwnd, rc);
    } return 0;
    case WM_NOTIFY: {
        LPNMHDR hdr = (LPNMHDR)lparam;
        if (hdr->idFrom == IDC_TAB && hdr->code == TCN_SELCHANGE) {
            int sel = TabCtrl_GetCurSel(GetDlgItem(hwnd, IDC_TAB));
    set_content_for_tab(sel, hwnd);
        }
    } break;
    case WM_APP_CONSOLE_APPEND: {
        HWND hconsole = g_console_edit;
        const wchar_t *text = (const wchar_t *)lparam;
        if (hconsole && text) {
            LRESULT len = GetWindowTextLengthW(hconsole);
            SendMessageW(hconsole, EM_SETSEL, len, len);
            SendMessageW(hconsole, EM_REPLACESEL, 0, (LPARAM)text);
        }
        if (text) free((void *)text);
        return 0;
    }
    case WM_ERASEBKGND: {
        RECT rc;
        GetClientRect(hwnd, &rc);
        FillRect((HDC)wparam, &rc, g_br_bg);
        return 1;
    }
    case WM_CTLCOLOREDIT:
    case WM_CTLCOLORSTATIC:
    case WM_CTLCOLORBTN: {
        HDC hdc = (HDC)wparam;
        HWND hCtl = (HWND)lparam;
        int id = GetDlgCtrlID(hCtl);
        SetBkMode(hdc, TRANSPARENT);
        SetTextColor(hdc, (id == IDC_LINKS) ? g_theme.link : g_theme.text);
        if (id == IDC_STATUS || id == IDC_BTN_PLAY || id == IDC_ACCOUNT_COMBO || id == IDC_INSTANCE_COMBO || id == IDC_PLATFORM_COMBO || id == IDC_UI_COMBO || id == IDC_RENDER_COMBO) {
            return (LRESULT)g_br_bottom;
        }
        return (LRESULT)g_br_panel;
    }
    case WM_COMMAND:
        if (LOWORD(wparam) == IDC_BTN_PLAY && HIWORD(wparam) == BN_CLICKED) {
            launch_game_impl(hwnd);
            return 0;
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    case WM_SETTINGCHANGE:
    case WM_THEMECHANGED:
        choose_theme();
        restyle_content(hwnd);
        return 0;
    default:
        break;
    }
    return DefWindowProc(hwnd, msg, wparam, lparam);
}

static HWND create_main_window(void)
{
    WNDCLASSW wc;
    HWND hwnd;
    wchar_t title[128];
    swprintf(title, sizeof(title)/sizeof(title[0]), L"%ls v%hs (build %d)", g_strings.title, DOM_LAUNCHER_VERSION, DOM_BUILD_NUMBER);

    memset(&wc, 0, sizeof(wc));
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = dom_launcher_wndproc;
    wc.hInstance = g_hinst;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_BTNFACE + 1);
    wc.lpszClassName = L"DomLauncherWin32";

    if (!RegisterClassW(&wc)) {
        return NULL;
    }

    hwnd = CreateWindowExW(
        0,
        wc.lpszClassName,
        title,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT,
        1024, 720,
        NULL, NULL, g_hinst, NULL);
    return hwnd;
}


/* New layout with explicit selectors */
static void create_children_new(HWND hwnd)
{
    HWND htab;
    HWND hnews;
    HWND hlinks;
    HWND haccount;
    HWND hinst_combo;
    HWND hplat_combo;
    HWND hui_combo;
    HWND hrend_combo;
    HWND hplay;
    HWND hstatus;
    TCITEMW item;
    RECT rc;

    htab = CreateWindowExW(0, WC_TABCONTROLW, L"",
                           WS_CHILD | WS_VISIBLE,
                           0, 0, 0, 0,
                           hwnd, (HMENU)(INT_PTR)IDC_TAB, g_hinst, NULL);
    set_font(htab);
    TabCtrl_SetItemSize(htab, 140, 28);
    memset(&item, 0, sizeof(item));
    item.mask = TCIF_TEXT;
    item.pszText = (LPWSTR)g_strings.tab_news; TabCtrl_InsertItem(htab, 0, &item);
    item.pszText = (LPWSTR)g_strings.tab_changes; TabCtrl_InsertItem(htab, 1, &item);
    item.pszText = (LPWSTR)g_strings.tab_mods; TabCtrl_InsertItem(htab, 2, &item);
    item.pszText = (LPWSTR)g_strings.tab_instances; TabCtrl_InsertItem(htab, 3, &item);
    item.pszText = (LPWSTR)g_strings.tab_settings; TabCtrl_InsertItem(htab, 4, &item);
    item.pszText = (LPWSTR)g_strings.tab_console; TabCtrl_InsertItem(htab, 5, &item);

    hnews = CreateWindowExW(WS_EX_CLIENTEDGE, MSFTEDIT_CLASS, L"",
                            WS_CHILD | WS_VISIBLE | ES_MULTILINE | ES_READONLY | WS_VSCROLL | ES_AUTOVSCROLL,
                            0, 0, 0, 0,
                            hwnd, (HMENU)(INT_PTR)IDC_NEWS, g_hinst, NULL);
    set_font(hnews);
    style_richedit(hnews, g_theme.panel, g_theme.text);
    populate_news(hnews);

    hlinks = CreateWindowExW(WS_EX_CLIENTEDGE, MSFTEDIT_CLASS, L"",
                             WS_CHILD | WS_VISIBLE | ES_MULTILINE | ES_READONLY | WS_VSCROLL | ES_AUTOVSCROLL,
                             0, 0, 0, 0,
                             hwnd, (HMENU)(INT_PTR)IDC_LINKS, g_hinst, NULL);
    set_font(hlinks);
    style_richedit(hlinks, g_theme.panel, g_theme.link);
    populate_links(hlinks);

    g_console_edit = CreateWindowExW(WS_EX_CLIENTEDGE, MSFTEDIT_CLASS, L"",
                                     WS_CHILD | WS_VISIBLE | ES_MULTILINE | ES_READONLY | WS_VSCROLL | ES_AUTOVSCROLL,
                                     0, 0, 0, 0,
                                     hwnd, (HMENU)(INT_PTR)IDC_CONSOLE, g_hinst, NULL);
    set_font(g_console_edit);
    style_richedit(g_console_edit, g_theme.panel, g_theme.text);
    ShowWindow(g_console_edit, SW_HIDE);

    haccount = CreateWindowExW(0, L"COMBOBOX", L"",
                               WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST,
                               0, 0, 0, 0,
                               hwnd, (HMENU)(INT_PTR)IDC_ACCOUNT_COMBO, g_hinst, NULL);
    set_font(haccount);
    SendMessageW(haccount, CB_ADDSTRING, 0, (LPARAM)L"Account A");
    SendMessageW(haccount, CB_ADDSTRING, 0, (LPARAM)L"Account B");
    SendMessageW(haccount, CB_SETCURSEL, 0, 0);

    hinst_combo = CreateWindowExW(0, L"COMBOBOX", L"",
                                  WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST,
                                  0, 0, 0, 0,
                                  hwnd, (HMENU)(INT_PTR)IDC_INSTANCE_COMBO, g_hinst, NULL);
    set_font(hinst_combo);
    SendMessageW(hinst_combo, CB_ADDSTRING, 0, (LPARAM)L"Instance 1");
    SendMessageW(hinst_combo, CB_ADDSTRING, 0, (LPARAM)L"Instance 2");
    SendMessageW(hinst_combo, CB_SETCURSEL, 0, 0);

    hplat_combo = CreateWindowExW(0, L"COMBOBOX", L"",
                                  WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST,
                                  0, 0, 0, 0,
                                  hwnd, (HMENU)(INT_PTR)IDC_PLATFORM_COMBO, g_hinst, NULL);
    set_font(hplat_combo);
    SendMessageW(hplat_combo, CB_ADDSTRING, 0, (LPARAM)L"Win32");
    SendMessageW(hplat_combo, CB_ADDSTRING, 0, (LPARAM)L"POSIX");
    SendMessageW(hplat_combo, CB_SETCURSEL, 0, 0);

    hui_combo = CreateWindowExW(0, L"COMBOBOX", L"",
                                WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST,
                                0, 0, 0, 0,
                                hwnd, (HMENU)(INT_PTR)IDC_UI_COMBO, g_hinst, NULL);
    set_font(hui_combo);
    SendMessageW(hui_combo, CB_ADDSTRING, 0, (LPARAM)L"GUI");
    SendMessageW(hui_combo, CB_ADDSTRING, 0, (LPARAM)L"TUI");
    SendMessageW(hui_combo, CB_ADDSTRING, 0, (LPARAM)L"CLI");
    SendMessageW(hui_combo, CB_SETCURSEL, 0, 0);

    hrend_combo = CreateWindowExW(0, L"COMBOBOX", L"",
                                  WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST,
                                  0, 0, 0, 0,
                                  hwnd, (HMENU)(INT_PTR)IDC_RENDER_COMBO, g_hinst, NULL);
    set_font(hrend_combo);
    SendMessageW(hrend_combo, CB_ADDSTRING, 0, (LPARAM)L"Software");
    SendMessageW(hrend_combo, CB_ADDSTRING, 0, (LPARAM)L"DX9");
    SendMessageW(hrend_combo, CB_ADDSTRING, 0, (LPARAM)L"GL1");
    SendMessageW(hrend_combo, CB_SETCURSEL, 0, 0);

    hplay = CreateWindowExW(0, L"BUTTON", g_strings.btn_play,
                            WS_CHILD | WS_VISIBLE,
                            0, 0, 0, 0,
                            hwnd, (HMENU)(INT_PTR)IDC_BTN_PLAY, g_hinst, NULL);
    set_font(hplay);

    hstatus = CreateWindowExW(0, L"STATIC", g_strings.status_ready,
                              WS_CHILD | WS_VISIBLE | SS_LEFT,
                              0, 0, 0, 0,
                              hwnd, (HMENU)(INT_PTR)IDC_STATUS, g_hinst, NULL);
    set_font(hstatus);

    GetClientRect(hwnd, &rc);
    layout_controls(hwnd, rc);
}
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow)
{
    MSG msg;
    HWND hwnd;
    INITCOMMONCONTROLSEX icc;
    (void)hPrevInstance;
    (void)lpCmdLine;

    g_hinst = hInstance;

    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_TAB_CLASSES | ICC_BAR_CLASSES | ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icc);
    LoadLibraryA("Msftedit.dll"); /* Rich edit */

    g_ui_font = (HFONT)GetStockObject(DEFAULT_GUI_FONT);
    choose_theme();

    hwnd = create_main_window();
    if (!hwnd) {
        return 1;
    }
    g_main_hwnd = hwnd;
    create_children_new(hwnd);
    set_content_for_tab(0, hwnd);
    restyle_content(hwnd);

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    while (GetMessage(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return (int)msg.wParam;
}
