// dom_setup CLI definitions.
#ifndef DOM_SETUP_CLI_H
#define DOM_SETUP_CLI_H

#include <string>

struct DomSetupInstallArgs {
    std::string mode;   /* portable | per-user | system */
    std::string target; /* optional target path */
    std::string version;
};

int dom_setup_cmd_install(const DomSetupInstallArgs &args);
int dom_setup_cmd_repair(const std::string &install_root);
int dom_setup_cmd_uninstall(const std::string &install_root, bool remove_user_data);
int dom_setup_cmd_list();
int dom_setup_cmd_info(const std::string &install_root);

void dom_setup_print_usage();

#endif /* DOM_SETUP_CLI_H */
