#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <commctrl.h>
#include <richedit.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>

#include "dom_build_version.h"

/* Launcher version (launcher-specific). */
#define DOM_LAUNCHER_VERSION "0.1.0"

/* Control IDs */
#define IDC_TAB           1001
#define IDC_NEWS          1002
#define IDC_LINKS         1003
#define IDC_PROFILE_COMBO 1004
#define IDC_BTN_NEW       1005
#define IDC_BTN_EDIT      1006
#define IDC_BTN_PLAY      1007
#define IDC_STATUS        1008
#define IDC_BTN_SWITCH    1009

static HFONT g_ui_font = NULL;
static HINSTANCE g_hinst = NULL;
static HBRUSH g_br_bg = NULL;
static HBRUSH g_br_panel = NULL;
static HBRUSH g_br_bottom = NULL;

/* Colors */
static const COLORREF kColorBg       = RGB(26, 26, 26);
static const COLORREF kColorPanel    = RGB(32, 32, 32);
static const COLORREF kColorBottom   = RGB(240, 240, 240);
static const COLORREF kColorText     = RGB(230, 230, 230);
static const COLORREF kColorLink     = RGB(120, 170, 255);

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
    HWND hcombo = GetDlgItem(hwnd, IDC_PROFILE_COMBO);
    HWND hnew = GetDlgItem(hwnd, IDC_BTN_NEW);
    HWND hedit = GetDlgItem(hwnd, IDC_BTN_EDIT);
    HWND hplay = GetDlgItem(hwnd, IDC_BTN_PLAY);
    HWND hstatus = GetDlgItem(hwnd, IDC_STATUS);
    HWND hswitch = GetDlgItem(hwnd, IDC_BTN_SWITCH);

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

    /* Bottom bar */
    MoveWindow(hcombo, padding, client.bottom - bottom_h + padding, 140, 24, TRUE);
    MoveWindow(hnew, padding, client.bottom - bottom_h + padding + 28, 90, 24, TRUE);
    MoveWindow(hedit, padding + 100, client.bottom - bottom_h + padding + 28, 90, 24, TRUE);

    MoveWindow(hplay,
               client.right / 2 - 80,
               client.bottom - bottom_h + padding,
               160,
               40,
               TRUE);

    MoveWindow(hstatus,
               client.right - right_panel_w - padding,
               client.bottom - bottom_h + padding,
               right_panel_w,
               24,
               TRUE);

    MoveWindow(hswitch,
               client.right - right_panel_w - padding,
               client.bottom - bottom_h + padding + 28,
               right_panel_w,
               24,
               TRUE);
}

static void populate_news(HWND hnews)
{
    static const char *news_utf8 =
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
        "We'll keep you posted.\n";
    int wlen;
    wchar_t *wtext;
    wlen = MultiByteToWideChar(CP_UTF8, 0, news_utf8, -1, NULL, 0);
    if (wlen <= 0) return;
    wtext = (wchar_t *)malloc((size_t)wlen * sizeof(wchar_t));
    if (!wtext) return;
    MultiByteToWideChar(CP_UTF8, 0, news_utf8, -1, wtext, wlen);
    SendMessageW(hnews, WM_SETTEXT, 0, (LPARAM)wtext);
    free(wtext);
}

static void populate_links(HWND hlinks)
{
    static const char *links_utf8 =
        "Official links:\n"
        "Dominium.net\n"
        "Forums\n"
        "Bug tracker\n"
        "Support\n"
        "Twitter\n"
        "Discord\n";
    int wlen = MultiByteToWideChar(CP_UTF8, 0, links_utf8, -1, NULL, 0);
    wchar_t *wtext;
    if (wlen <= 0) return;
    wtext = (wchar_t *)malloc((size_t)wlen * sizeof(wchar_t));
    if (!wtext) return;
    MultiByteToWideChar(CP_UTF8, 0, links_utf8, -1, wtext, wlen);
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

static LRESULT CALLBACK dom_launcher_wndproc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
{
    switch (msg) {
    case WM_SIZE: {
        RECT rc;
        GetClientRect(hwnd, &rc);
        layout_controls(hwnd, rc);
    } return 0;
    case WM_ERASEBKGND: {
        RECT rc;
        GetClientRect(hwnd, &rc);
        FillRect((HDC)wparam, &rc, g_br_bg);
        return 1;
    }
    case WM_CTLCOLOREDIT:
    case WM_CTLCOLORSTATIC: {
        HDC hdc = (HDC)wparam;
        HWND hCtl = (HWND)lparam;
        int id = GetDlgCtrlID(hCtl);
        SetBkMode(hdc, TRANSPARENT);
        SetTextColor(hdc, (id == IDC_LINKS) ? kColorLink : kColorText);
        if (id == IDC_STATUS || id == IDC_BTN_SWITCH || id == IDC_BTN_NEW || id == IDC_BTN_EDIT || id == IDC_BTN_PLAY || id == IDC_PROFILE_COMBO) {
            return (LRESULT)g_br_bottom;
        }
        return (LRESULT)g_br_panel;
    }
    case WM_DESTROY:
        PostQuitMessage(0);
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
    swprintf(title, sizeof(title)/sizeof(title[0]), L"Dominium Launcher v%hs (build %d)", DOM_LAUNCHER_VERSION, DOM_BUILD_NUMBER);

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

static void create_children(HWND hwnd)
{
    HWND htab;
    HWND hnews;
    HWND hlinks;
    HWND hcombo;
    HWND hnew;
    HWND hedit;
    HWND hplay;
    HWND hstatus;
    HWND hswitch;
    TCITEMW item;
    RECT rc;

    /* Tab control */
    htab = CreateWindowExW(0, WC_TABCONTROLW, L"",
                           WS_CHILD | WS_VISIBLE,
                           0, 0, 0, 0,
                           hwnd, (HMENU)(INT_PTR)IDC_TAB, g_hinst, NULL);
    set_font(htab);
    TabCtrl_SetItemSize(htab, 120, 24);
    item.mask = TCIF_TEXT;
    item.pszText = L"Update Notes";
    TabCtrl_InsertItem(htab, 0, &item);
    item.pszText = L"Launcher Log";
    TabCtrl_InsertItem(htab, 1, &item);
    item.pszText = L"Profile Editor";
    TabCtrl_InsertItem(htab, 2, &item);

    /* News RichEdit */
    hnews = CreateWindowExW(WS_EX_CLIENTEDGE, MSFTEDIT_CLASS, L"",
                            WS_CHILD | WS_VISIBLE | ES_MULTILINE | ES_READONLY | WS_VSCROLL | ES_AUTOVSCROLL,
                            0, 0, 0, 0,
                            hwnd, (HMENU)(INT_PTR)IDC_NEWS, g_hinst, NULL);
    set_font(hnews);
    style_richedit(hnews, kColorPanel, kColorText);
    populate_news(hnews);

    /* Links RichEdit (read-only) */
    hlinks = CreateWindowExW(WS_EX_CLIENTEDGE, MSFTEDIT_CLASS, L"",
                             WS_CHILD | WS_VISIBLE | ES_MULTILINE | ES_READONLY | WS_VSCROLL | ES_AUTOVSCROLL,
                             0, 0, 0, 0,
                             hwnd, (HMENU)(INT_PTR)IDC_LINKS, g_hinst, NULL);
    set_font(hlinks);
    style_richedit(hlinks, kColorPanel, kColorLink);
    populate_links(hlinks);

    /* Bottom controls */
    hcombo = CreateWindowExW(0, L"COMBOBOX", L"",
                             WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST,
                             0, 0, 0, 0,
                             hwnd, (HMENU)(INT_PTR)IDC_PROFILE_COMBO, g_hinst, NULL);
    set_font(hcombo);
    SendMessageW(hcombo, CB_ADDSTRING, 0, (LPARAM)L"Default");
    SendMessageW(hcombo, CB_ADDSTRING, 0, (LPARAM)L"Profile A");
    SendMessageW(hcombo, CB_SETCURSEL, 0, 0);

    hnew = CreateWindowExW(0, L"BUTTON", L"New Profile",
                           WS_CHILD | WS_VISIBLE,
                           0, 0, 0, 0,
                           hwnd, (HMENU)(INT_PTR)IDC_BTN_NEW, g_hinst, NULL);
    set_font(hnew);

    hedit = CreateWindowExW(0, L"BUTTON", L"Edit Profile",
                            WS_CHILD | WS_VISIBLE,
                            0, 0, 0, 0,
                            hwnd, (HMENU)(INT_PTR)IDC_BTN_EDIT, g_hinst, NULL);
    set_font(hedit);

    hplay = CreateWindowExW(0, L"BUTTON", L"Play",
                            WS_CHILD | WS_VISIBLE,
                            0, 0, 0, 0,
                            hwnd, (HMENU)(INT_PTR)IDC_BTN_PLAY, g_hinst, NULL);
    set_font(hplay);

    hstatus = CreateWindowExW(0, L"STATIC", L"Ready to update & play Dominium",
                              WS_CHILD | WS_VISIBLE | SS_LEFT,
                              0, 0, 0, 0,
                              hwnd, (HMENU)(INT_PTR)IDC_STATUS, g_hinst, NULL);
    set_font(hstatus);

    hswitch = CreateWindowExW(0, L"BUTTON", L"Switch User",
                              WS_CHILD | WS_VISIBLE,
                              0, 0, 0, 0,
                              hwnd, (HMENU)(INT_PTR)IDC_BTN_SWITCH, g_hinst, NULL);
    set_font(hswitch);

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
    g_br_bg = CreateSolidBrush(kColorBg);
    g_br_panel = CreateSolidBrush(kColorPanel);
    g_br_bottom = CreateSolidBrush(kColorBottom);

    hwnd = create_main_window();
    if (!hwnd) {
        return 1;
    }
    create_children(hwnd);

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    while (GetMessage(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return (int)msg.wParam;
}
