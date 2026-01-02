cmake_minimum_required(VERSION 3.16)

add_executable(dominium-setup-steam
    dominium_setup_steam_main.cpp
)

set_target_properties(dominium-setup-steam PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

add_custom_target(build-steam-provider
    DEPENDS dominium-setup-steam
)
