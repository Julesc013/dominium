// Small filesystem helpers used by dom_setup and tests.
#ifndef DOM_SETUP_FS_H
#define DOM_SETUP_FS_H

#include <string>
#include <vector>

bool dom_fs_path_exists(const std::string &path);
bool dom_fs_is_dir(const std::string &path);
bool dom_fs_make_dirs(const std::string &path);
bool dom_fs_remove_tree(const std::string &path);
bool dom_fs_copy_file(const std::string &src, const std::string &dst);
std::vector<std::string> dom_fs_list_dir(const std::string &path);

#endif /* DOM_SETUP_FS_H */
