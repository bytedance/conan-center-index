cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(fbthrift CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)

# TODO:
# thrift_library(
#     ${PROJECT_NAME}_thrift
#       TestPackageThrift
#       cpp2
#       ""
#       ${CMAKE_CURRENT_SOURCE_DIR}
#       ${CMAKE_CURRENT_BINARY_DIR}
#       "..")

# target_link_libraries(${PROJECT_NAME}_thrift-cpp2 fbthrift::fbthrift)
# target_include_directories(${PROJECT_NAME}_thrift-cpp2-obj SYSTEM
#           PUBLIC
#            ${CMAKE_CURRENT_BINARY_DIR}
# )

# add_dependencies(${PROJECT_NAME}
#     ${PROJECT_NAME}_thrift-cpp2)