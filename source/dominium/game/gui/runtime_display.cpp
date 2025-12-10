#include "runtime_display.h"
#include <cstring>

#ifdef _WIN32
#include <io.h>
#define ISATTY _isatty
#define FILENO _fileno
#else
#include <unistd.h>
#define ISATTY isatty
#define FILENO fileno
#endif

DomDisplayMode parse_display_mode(const std::string &display, bool is_tty)
{
    if (display == "none") return DOM_DISPLAY_NONE;
    if (display == "cli") return DOM_DISPLAY_CLI;
    if (display == "tui") return DOM_DISPLAY_TUI;
    if (display == "gui") return DOM_DISPLAY_GUI;
    /* auto */
    if (is_tty) return DOM_DISPLAY_TUI;
    return DOM_DISPLAY_NONE;
}
