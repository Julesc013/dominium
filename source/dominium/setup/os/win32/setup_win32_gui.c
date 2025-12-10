#include <windows.h>
#include <shlobj.h>
#include <commctrl.h>
#include <stdio.h>
#include <string.h>

#define IDC_SCOPE_PORTABLE   1001
#define IDC_SCOPE_USER       1002
#define IDC_SCOPE_SYSTEM     1003
#define IDC_EDIT_PATH        1004
#define IDC_BUTTON_BROWSE    1005
#define IDC_BUTTON_INSTALL   1006
#define IDC_BUTTON_REPAIR    1007
#define IDC_BUTTON_UNINSTALL 1008
#define IDC_BUTTON_VERIFY    1009
#define IDC_PROGRESS         1010
#define IDC_STATUS           1011
#define IDC_BUTTON_BACK      1200
#define IDC_BUTTON_NEXT      1201
#define IDC_BUTTON_CANCEL    1202
#define IDC_LABEL_INTRO      1300
#define IDC_LABEL_DETAILS    1301
#define IDC_LABEL_SCOPE      1302
#define IDC_LABEL_PATH       1303
#define IDC_LABEL_ACTIONS    1304

#define WM_APP_SETUP_DONE (WM_APP + 1)
#define COUNTOF(x) (sizeof(x) / sizeof((x)[0]))

typedef struct setup_thread_args_t {
    HWND  hwnd;
    char  command_line[1024];
} setup_thread_args_t;

static HWND g_edit_path = NULL;
static HWND g_progress = NULL;
static HWND g_status = NULL;
static HWND g_button_back = NULL;
static HWND g_button_next = NULL;
static HWND g_button_cancel = NULL;
static char g_cli_path[MAX_PATH];
static int g_current_page = 0;
static int g_action_running = 0;

static const int kOptionsControls[] = {
    IDC_LABEL_INTRO,
    IDC_LABEL_DETAILS,
    IDC_LABEL_SCOPE,
    IDC_SCOPE_PORTABLE,
    IDC_SCOPE_USER,
    IDC_SCOPE_SYSTEM,
    IDC_LABEL_PATH,
    IDC_EDIT_PATH,
    IDC_BUTTON_BROWSE
};

static const int kActionControls[] = {
    IDC_LABEL_ACTIONS,
    IDC_BUTTON_INSTALL,
    IDC_BUTTON_REPAIR,
    IDC_BUTTON_UNINSTALL,
    IDC_BUTTON_VERIFY,
    IDC_PROGRESS,
    IDC_STATUS
};

static void center_window(HWND hwnd)
{
    RECT rc;
    RECT rc_parent;
    int  x;
    int  y;
    HWND parent;

    parent = GetDesktopWindow();
    GetWindowRect(hwnd, &rc);
    GetWindowRect(parent, &rc_parent);

    x = ((rc_parent.right - rc_parent.left) - (rc.right - rc.left)) / 2;
    y = ((rc_parent.bottom - rc_parent.top) - (rc.bottom - rc.top)) / 2;
    SetWindowPos(hwnd, NULL, x, y, 0, 0, SWP_NOZORDER | SWP_NOSIZE);
}

static void set_status_text(const char* text)
{
    if (g_status && text) {
        SetWindowTextA(g_status, text);
    }
}

static void update_nav_buttons(void)
{
    if (g_button_back) {
        EnableWindow(g_button_back, !g_action_running && g_current_page > 0);
    }
    if (g_button_next) {
        SetWindowTextA(g_button_next, g_current_page == 0 ? "Next >" : "Finish");
        EnableWindow(g_button_next, !g_action_running);
    }
    if (g_button_cancel) {
        EnableWindow(g_button_cancel, !g_action_running);
    }
}

static void get_default_target_dir(char* buf, size_t cap)
{
    char base[MAX_PATH];
    size_t len;

    if (!buf || cap == 0u) {
        return;
    }
    buf[0] = '\0';

    if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_LOCAL_APPDATA, NULL, SHGFP_TYPE_CURRENT, base))) {
        lstrcpynA(buf, base, (int)cap);
        len = strlen(buf);
        if (len + 20u < cap) {
            lstrcatA(buf, "\\Programs\\Dominium");
        } else {
            buf[cap - 1u] = '\0';
        }
    } else {
        lstrcpynA(buf, "C:\\Dominium", (int)cap);
    }
}

static void get_cli_path(char* buf, size_t cap)
{
    DWORD len;
    size_t i;

    if (!buf || cap == 0u) {
        return;
    }
    buf[0] = '\0';

    len = GetModuleFileNameA(NULL, buf, (DWORD)cap);
    if (len == 0 || len >= cap) {
        lstrcpynA(buf, "dominium-setup-cli.exe", (int)cap);
        return;
    }

    for (i = len; i > 0; --i) {
        if (buf[i - 1] == '\\' || buf[i - 1] == '/') {
            buf[i] = '\0';
            break;
        }
    }
    lstrcatA(buf, "dominium-setup-cli.exe");
}

static void enable_action_buttons(HWND hwnd, int enable)
{
    EnableWindow(GetDlgItem(hwnd, IDC_BUTTON_INSTALL), enable);
    EnableWindow(GetDlgItem(hwnd, IDC_BUTTON_REPAIR), enable);
    EnableWindow(GetDlgItem(hwnd, IDC_BUTTON_UNINSTALL), enable);
    EnableWindow(GetDlgItem(hwnd, IDC_BUTTON_VERIFY), enable);
    EnableWindow(GetDlgItem(hwnd, IDC_BUTTON_BROWSE), enable);
    EnableWindow(GetDlgItem(hwnd, IDC_EDIT_PATH), enable);
    EnableWindow(GetDlgItem(hwnd, IDC_SCOPE_PORTABLE), enable);
    EnableWindow(GetDlgItem(hwnd, IDC_SCOPE_USER), enable);
    EnableWindow(GetDlgItem(hwnd, IDC_SCOPE_SYSTEM), enable);
}

static void start_progress(void)
{
    if (g_progress) {
        SendMessage(g_progress, PBM_SETMARQUEE, TRUE, 0);
        ShowWindow(g_progress, SW_SHOW);
    }
}

static void stop_progress(void)
{
    if (g_progress) {
        SendMessage(g_progress, PBM_SETMARQUEE, FALSE, 0);
        ShowWindow(g_progress, SW_HIDE);
    }
}

static void browse_for_folder(HWND owner)
{
    BROWSEINFOA bi;
    LPITEMIDLIST pidl;
    char path[MAX_PATH];

    ZeroMemory(&bi, sizeof(bi));
    bi.hwndOwner = owner;
    bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE;
    bi.lpszTitle = "Choose install folder";

    pidl = SHBrowseForFolderA(&bi);
    if (pidl && SHGetPathFromIDListA(pidl, path)) {
        SetWindowTextA(g_edit_path, path);
    }
    if (pidl) {
        CoTaskMemFree(pidl);
    }
}

static void show_page(HWND hwnd, int page)
{
    size_t i;

    g_current_page = page;
    for (i = 0; i < COUNTOF(kOptionsControls); ++i) {
        ShowWindow(GetDlgItem(hwnd, kOptionsControls[i]), page == 0 ? SW_SHOW : SW_HIDE);
    }
    for (i = 0; i < COUNTOF(kActionControls); ++i) {
        ShowWindow(GetDlgItem(hwnd, kActionControls[i]), page == 1 ? SW_SHOW : SW_HIDE);
    }

    if (page == 0) {
        SetFocus(GetDlgItem(hwnd, IDC_SCOPE_USER));
    } else {
        SetFocus(GetDlgItem(hwnd, IDC_BUTTON_INSTALL));
    }
    update_nav_buttons();
}

static void build_scope_string(HWND hwnd, char* buf, size_t cap)
{
    if (!buf || cap == 0u) {
        return;
    }
    buf[0] = '\0';
    if (IsDlgButtonChecked(hwnd, IDC_SCOPE_PORTABLE) == BST_CHECKED) {
        lstrcpynA(buf, "portable", (int)cap);
    } else if (IsDlgButtonChecked(hwnd, IDC_SCOPE_SYSTEM) == BST_CHECKED) {
        lstrcpynA(buf, "system", (int)cap);
    } else {
        lstrcpynA(buf, "user", (int)cap);
    }
}

static DWORD WINAPI setup_thread_proc(LPVOID param)
{
    setup_thread_args_t* args;
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    BOOL created;
    DWORD exit_code;
    DWORD wait_res;

    args = (setup_thread_args_t*)param;
    if (!args) {
        return 1;
    }

    ZeroMemory(&si, sizeof(si));
    ZeroMemory(&pi, sizeof(pi));
    si.cb = sizeof(si);

    created = CreateProcessA(NULL,
                             args->command_line,
                             NULL,
                             NULL,
                             FALSE,
                             CREATE_NO_WINDOW,
                             NULL,
                             NULL,
                             &si,
                             &pi);
    if (!created) {
        PostMessage(args->hwnd, WM_APP_SETUP_DONE, (WPARAM)1, 0);
        HeapFree(GetProcessHeap(), 0, args);
        return 1;
    }

    wait_res = WaitForSingleObject(pi.hProcess, INFINITE);
    (void)wait_res;

    exit_code = 1;
    GetExitCodeProcess(pi.hProcess, &exit_code);

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);

    PostMessage(args->hwnd, WM_APP_SETUP_DONE, (WPARAM)exit_code, 0);
    HeapFree(GetProcessHeap(), 0, args);
    return 0;
}

static void start_setup_action(HWND hwnd, const char* action)
{
    char scope[32];
    char target[MAX_PATH];
    char cmd[1024];
    setup_thread_args_t* args;

    if (!action) {
        return;
    }

    build_scope_string(hwnd, scope, sizeof(scope));
    GetWindowTextA(g_edit_path, target, (int)sizeof(target));

    wsprintfA(cmd, "\"%s\" --scope=%s --action=%s --dir=\"%s\"",
              g_cli_path, scope, action, target);

    args = (setup_thread_args_t*)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(setup_thread_args_t));
    if (!args) {
        MessageBoxA(hwnd, "Out of memory", "Dominium Setup", MB_ICONERROR | MB_OK);
        return;
    }
    args->hwnd = hwnd;
    lstrcpynA(args->command_line, cmd, (int)sizeof(args->command_line));

    enable_action_buttons(hwnd, FALSE);
    start_progress();
    set_status_text("Running dominium-setup-cli...");
    g_action_running = 1;
    update_nav_buttons();

    if (!CreateThread(NULL, 0, setup_thread_proc, args, 0, NULL)) {
        stop_progress();
        enable_action_buttons(hwnd, TRUE);
        set_status_text("Failed to start setup process");
        HeapFree(GetProcessHeap(), 0, args);
        g_action_running = 0;
        update_nav_buttons();
    }
}

static LRESULT CALLBACK main_wnd_proc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg) {
    case WM_CREATE:
        {
            char default_path[MAX_PATH];
            RECT rc_client;
            int left;
            int top;
            int nav_y;
            int content_width;

            GetClientRect(hwnd, &rc_client);
            left = 16;
            top = 16;
            content_width = rc_client.right - rc_client.left - 32;

            CreateWindowExA(0, "STATIC", "Welcome to Dominium Setup", WS_CHILD | WS_VISIBLE | SS_LEFT,
                            left, top, content_width, 20, hwnd, (HMENU)IDC_LABEL_INTRO, NULL, NULL);
            top += 20;
            CreateWindowExA(0, "STATIC", "Choose install scope and destination, then pick an action.",
                            WS_CHILD | WS_VISIBLE | SS_LEFT,
                            left, top, content_width, 18, hwnd, (HMENU)IDC_LABEL_DETAILS, NULL, NULL);

            top += 28;
            CreateWindowExA(0, "STATIC", "Scope:", WS_CHILD | WS_VISIBLE | SS_LEFT,
                            left, top + 2, 60, 18, hwnd, (HMENU)IDC_LABEL_SCOPE, NULL, NULL);
            CreateWindowExA(0, "BUTTON", "Portable", WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON,
                            left + 70, top, 90, 20, hwnd, (HMENU)IDC_SCOPE_PORTABLE, NULL, NULL);
            CreateWindowExA(0, "BUTTON", "Per-user", WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON,
                            left + 170, top, 90, 20, hwnd, (HMENU)IDC_SCOPE_USER, NULL, NULL);
            CreateWindowExA(0, "BUTTON", "All users", WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON,
                            left + 270, top, 90, 20, hwnd, (HMENU)IDC_SCOPE_SYSTEM, NULL, NULL);
            CheckDlgButton(hwnd, IDC_SCOPE_USER, BST_CHECKED);

            top += 30;
            CreateWindowExA(0, "STATIC", "Install directory:", WS_CHILD | WS_VISIBLE | SS_LEFT,
                            left, top + 2, 100, 20, hwnd, (HMENU)IDC_LABEL_PATH, NULL, NULL);
            g_edit_path = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "",
                                          WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                          left + 110, top, content_width - 90, 22,
                                          hwnd, (HMENU)IDC_EDIT_PATH, NULL, NULL);
            CreateWindowExA(0, "BUTTON", "Browse...", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                            rc_client.right - rc_client.left - 80, top - 1, 70, 24,
                            hwnd, (HMENU)IDC_BUTTON_BROWSE, NULL, NULL);

            top += 50;
            CreateWindowExA(0, "STATIC", "Choose maintenance action:", WS_CHILD | WS_VISIBLE | SS_LEFT,
                            left, top, content_width, 18, hwnd, (HMENU)IDC_LABEL_ACTIONS, NULL, NULL);

            top += 26;
            CreateWindowExA(0, "BUTTON", "Install", WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON,
                            left, top, 100, 26, hwnd, (HMENU)IDC_BUTTON_INSTALL, NULL, NULL);
            CreateWindowExA(0, "BUTTON", "Repair", WS_CHILD | WS_VISIBLE,
                            left + 110, top, 100, 26, hwnd, (HMENU)IDC_BUTTON_REPAIR, NULL, NULL);
            CreateWindowExA(0, "BUTTON", "Uninstall", WS_CHILD | WS_VISIBLE,
                            left + 220, top, 100, 26, hwnd, (HMENU)IDC_BUTTON_UNINSTALL, NULL, NULL);
            CreateWindowExA(0, "BUTTON", "Verify", WS_CHILD | WS_VISIBLE,
                            left + 330, top, 100, 26, hwnd, (HMENU)IDC_BUTTON_VERIFY, NULL, NULL);

            top += 40;
            g_progress = CreateWindowExA(0, PROGRESS_CLASSA, "",
                                         WS_CHILD | WS_VISIBLE | PBS_MARQUEE,
                                         left, top, content_width, 18,
                                         hwnd, (HMENU)IDC_PROGRESS, NULL, NULL);
            stop_progress();

            top += 26;
            g_status = CreateWindowExA(0, "STATIC", "Ready", WS_CHILD | WS_VISIBLE,
                                       left, top, content_width, 20,
                                       hwnd, (HMENU)IDC_STATUS, NULL, NULL);

            nav_y = rc_client.bottom - rc_client.top - 40;
            g_button_back = CreateWindowExA(0, "BUTTON", "< Back", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                                            left, nav_y, 90, 26, hwnd, (HMENU)IDC_BUTTON_BACK, NULL, NULL);
            g_button_next = CreateWindowExA(0, "BUTTON", "Next >", WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON,
                                            rc_client.right - rc_client.left - 190, nav_y, 90, 26,
                                            hwnd, (HMENU)IDC_BUTTON_NEXT, NULL, NULL);
            g_button_cancel = CreateWindowExA(0, "BUTTON", "Cancel", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                                              rc_client.right - rc_client.left - 95, nav_y, 80, 26,
                                              hwnd, (HMENU)IDC_BUTTON_CANCEL, NULL, NULL);

            get_default_target_dir(default_path, sizeof(default_path));
            SetWindowTextA(g_edit_path, default_path);
            show_page(hwnd, 0);
            stop_progress();
            set_status_text("Ready");
        }
        break;
    case WM_COMMAND:
        switch (LOWORD(wParam)) {
        case IDC_BUTTON_BROWSE:
            browse_for_folder(hwnd);
            break;
        case IDC_BUTTON_INSTALL:
            start_setup_action(hwnd, "install");
            break;
        case IDC_BUTTON_REPAIR:
            start_setup_action(hwnd, "repair");
            break;
        case IDC_BUTTON_UNINSTALL:
            start_setup_action(hwnd, "uninstall");
            break;
        case IDC_BUTTON_VERIFY:
            start_setup_action(hwnd, "verify");
            break;
        case IDC_BUTTON_NEXT:
            if (g_current_page == 0) {
                show_page(hwnd, 1);
            } else if (!g_action_running) {
                PostMessage(hwnd, WM_CLOSE, 0, 0);
            }
            break;
        case IDC_BUTTON_BACK:
            if (g_current_page > 0 && !g_action_running) {
                show_page(hwnd, g_current_page - 1);
            }
            break;
        case IDC_BUTTON_CANCEL:
            if (!g_action_running) {
                PostMessage(hwnd, WM_CLOSE, 0, 0);
            }
            break;
        default:
            break;
        }
        break;
    case WM_APP_SETUP_DONE:
        stop_progress();
        enable_action_buttons(hwnd, TRUE);
        g_action_running = 0;
        update_nav_buttons();
        if ((DWORD)wParam == 0) {
            set_status_text("Finished successfully.");
            MessageBoxA(hwnd, "Operation completed successfully.", "Dominium Setup", MB_ICONINFORMATION | MB_OK);
        } else {
            set_status_text("Setup reported an error.");
            MessageBoxA(hwnd, "dominium-setup-cli failed. Check logs or run manually for details.",
                        "Dominium Setup", MB_ICONERROR | MB_OK);
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}

int APIENTRY WinMain(HINSTANCE hInstance,
                     HINSTANCE hPrevInstance,
                     LPSTR     lpCmdLine,
                     int       nCmdShow)
{
    WNDCLASSA wc;
    HWND hwnd;
    MSG msg;
    INITCOMMONCONTROLSEX icc;

    (void)hPrevInstance;
    (void)lpCmdLine;

    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_PROGRESS_CLASS;
    InitCommonControlsEx(&icc);

    ZeroMemory(&wc, sizeof(wc));
    wc.lpfnWndProc = main_wnd_proc;
    wc.hInstance = hInstance;
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = "DominiumSetupWin32Class";
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);

    if (!RegisterClassA(&wc)) {
        MessageBoxA(NULL, "Failed to register window class", "Dominium Setup", MB_ICONERROR | MB_OK);
        return 1;
    }

    hwnd = CreateWindowExA(0,
                          wc.lpszClassName,
                          "Dominium Setup",
                          WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
                          CW_USEDEFAULT, CW_USEDEFAULT,
                          620, 360,
                          NULL, NULL,
                          hInstance,
                          NULL);
    if (!hwnd) {
        MessageBoxA(NULL, "Failed to create window", "Dominium Setup", MB_ICONERROR | MB_OK);
        return 1;
    }

    center_window(hwnd);
    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    get_cli_path(g_cli_path, sizeof(g_cli_path));
    set_status_text("Ready");

    while (GetMessage(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return (int)msg.wParam;
}
