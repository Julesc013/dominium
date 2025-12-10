#ifndef DOMINIUM_GAME_APP_HPP
#define DOMINIUM_GAME_APP_HPP

class GameApp {
public:
    GameApp();
    ~GameApp();

    int run(int argc, char** argv);

private:
    int run_headless(int argc, char** argv);
};

#endif /* DOMINIUM_GAME_APP_HPP */
