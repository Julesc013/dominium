#ifndef DOMINIUM_LAUNCHER_APP_HPP
#define DOMINIUM_LAUNCHER_APP_HPP

class LauncherApp {
public:
    LauncherApp();
    ~LauncherApp();

    int run(int argc, char** argv);

private:
    int run_list_products();
    int run_run_game(int argc, char** argv);
};

#endif /* DOMINIUM_LAUNCHER_APP_HPP */
