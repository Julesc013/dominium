#ifndef DOM_LAUNCHER_UI_GUI_H
#define DOM_LAUNCHER_UI_GUI_H

namespace dom_launcher {

// GUI launcher entry. Returns 0 on success, non-zero to trigger fallback.
int launcher_run_gui(int argc, char** argv);

} // namespace dom_launcher

#endif
