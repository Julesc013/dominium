cmake_minimum_required(VERSION 3.16)

add_executable(dominium-setup2-steam
    dominium_setup2_steam_main.cpp
)

set_target_properties(dominium-setup2-steam PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_custom_target(build-steam-provider
    DEPENDS dominium-setup2-steam
)
