cmake_minimum_required(VERSION 3.18)
project(cpp_energy LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(cpp_energy
  src/energy_bindings.cpp
  src/charge_curve.cpp
)

target_include_directories(cpp_energy PRIVATE src)