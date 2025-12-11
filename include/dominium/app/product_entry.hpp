#ifndef DOMINIUM_APP_PRODUCT_ENTRY_HPP
#define DOMINIUM_APP_PRODUCT_ENTRY_HPP

extern "C" {

struct d_app_params; /* forward from Domino C header */

int dom_launcher_run_cli(const d_app_params* p);
int dom_launcher_run_tui(const d_app_params* p);
int dom_launcher_run_gui(const d_app_params* p);

int dom_game_run_cli(const d_app_params* p);
int dom_game_run_tui(const d_app_params* p);
int dom_game_run_gui(const d_app_params* p);
int dom_game_run_headless(const d_app_params* p);

int dom_setup_run_cli(const d_app_params* p);
int dom_setup_run_tui(const d_app_params* p);
int dom_setup_run_gui(const d_app_params* p);

int dom_tools_run_cli(const d_app_params* p);
int dom_tools_run_tui(const d_app_params* p);
int dom_tools_run_gui(const d_app_params* p);

} /* extern \"C\" */

#endif
