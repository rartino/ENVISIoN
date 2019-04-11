#--------------------------------------------------------------------
# Inviwo graph2d Module
ivw_module(graph2d)

#--------------------------------------------------------------------
# Add header files
set(HEADER_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/datastructures/graph2ddata.h
    ${CMAKE_CURRENT_SOURCE_DIR}/datastructures/geometry/linemesh.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/functionoperationnary.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/functionoperationunary.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/functiontodataframe.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5pathselectionallchildren.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5pathselectionint.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5pathselectionintvector.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5tofunction.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5topoint.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/lineplotprocessor.h
    ${CMAKE_CURRENT_SOURCE_DIR}/util/stringcomparenatural.h
    )

ivw_group("Header Files" ${HEADER_FILES})

#--------------------------------------------------------------------
# Add source files
set(SOURCE_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/datastructures/graph2ddata.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/datastructures/geometry/linemesh.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/functionoperationnary.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/functionoperationunary.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/functiontodataframe.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5pathselectionallchildren.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5pathselectionint.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5pathselectionintvector.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5tofunction.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/hdf5topoint.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/lineplotprocessor.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/util/stringcomparenatural.cpp
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

