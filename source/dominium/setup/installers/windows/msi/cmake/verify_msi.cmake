if(NOT DEFINED MSI_PATH)
    message(FATAL_ERROR "verify_msi.cmake: MSI_PATH not set")
endif()

if(NOT EXISTS "${MSI_PATH}")
    message(FATAL_ERROR "verify_msi.cmake: MSI not found: ${MSI_PATH}")
endif()

file(SIZE "${MSI_PATH}" _msi_size)
if(_msi_size LESS 1024)
    message(FATAL_ERROR "verify_msi.cmake: MSI too small: ${MSI_PATH}")
endif()

message(STATUS "verify_msi.cmake: verified ${MSI_PATH} (${_msi_size} bytes)")
