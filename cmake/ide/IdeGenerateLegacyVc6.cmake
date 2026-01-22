function(dom_ide_generate_legacy_vc6 out_dir project_name sources_var)
    file(MAKE_DIRECTORY "${out_dir}")
    set(_target_type "Win32 (x86) Application")
    set(_target_hex "0x0101")
    if(DOM_PRODUCT STREQUAL "engine" OR DOM_PRODUCT STREQUAL "game")
        set(_target_type "Win32 (x86) Static Library")
        set(_target_hex "0x0104")
    endif()

    set(_source_block "")
    foreach(_src IN LISTS ${sources_var})
        file(TO_NATIVE_PATH "${_src}" _native)
        string(APPEND _source_block "# Begin Source File\n")
        string(APPEND _source_block "SOURCE=${_native}\n")
        string(APPEND _source_block "# End Source File\n")
    endforeach()

    set(DOM_IDE_VC6_PROJECT_NAME "${project_name}")
    set(DOM_IDE_VC6_TARGET_TYPE "${_target_type}")
    set(DOM_IDE_VC6_TARGET_HEX "${_target_hex}")
    set(DOM_IDE_VC6_SOURCE_BLOCK "${_source_block}")
    configure_file(
        "${CMAKE_SOURCE_DIR}/cmake/ide/templates/vc6/vc6_project.dsp.in"
        "${out_dir}/${project_name}.dsp"
        @ONLY
    )
    configure_file(
        "${CMAKE_SOURCE_DIR}/cmake/ide/templates/vc6/vc6_workspace.dsw.in"
        "${out_dir}/${project_name}.dsw"
        @ONLY
    )
endfunction()
