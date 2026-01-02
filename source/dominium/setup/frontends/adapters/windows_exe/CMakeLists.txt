cmake_minimum_required(VERSION 3.16)

if(WIN32)
    add_executable(dominium-setup-win-exe
        dominium_setup_win_exe_main.cpp
    )
    set_target_properties(dominium-setup-win-exe PROPERTIES
        CXX_STANDARD 98
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
    )
    add_custom_target(build-windows-exe-adapter
        DEPENDS dominium-setup-win-exe
    )
else()
    add_custom_target(build-windows-exe-adapter)
endif()
