#--------------------------------------------------------------------
# Inviwo lineplot Module
ivw_module(lineplot)

#--------------------------------------------------------------------
# Add header files
set(HEADER_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5todataframe.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/lineplotprocessor.h
    )

ivw_group("Header Files" ${HEADER_FILES})

#--------------------------------------------------------------------
# Add source files
set(SOURCE_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5todataframe.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/lineplotprocessor.cpp
    )

ivw_group("Source Files" ${SOURCE_FILES})


#--------------------------------------------------------------------
# Add shaders
set(SHADER_FILES  
)
ivw_group("Shader Files" ${SHADER_FILES})


#--------------------------------------------------------------------
# Add Unittests
set(TEST_FILES
)
ivw_add_unittest(${TEST_FILES})

#--------------------------------------------------------------------
# Create module
ivw_create_module(${SOURCE_FILES} ${HEADER_FILES} ${SHADER_FILES})

