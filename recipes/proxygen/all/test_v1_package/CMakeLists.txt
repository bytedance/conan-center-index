cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(proxygen REQUIRED CONFIG)
find_package(folly REQUIRED CONFIG)
find_package(wangle REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)

target_link_libraries(${PROJECT_NAME}
    PUBLIC
    proxygen::proxygenhttpserver
    wangle::wangle
    Folly::folly)