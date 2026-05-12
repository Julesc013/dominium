# Engine Core Dominium Quarantine

These source files were removed from the engine build because they include
game-layer headers (`dominium/*`), which violates engine purity. They remain
here for reference until their responsibilities are moved into the game layer
or a neutral contract surface.
