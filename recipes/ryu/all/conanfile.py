# Copyright (c) ByteDance Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches
from conan.tools import scm
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.microsoft import is_msvc

import os


class RyuConan(ConanFile):
    name = "ryu"
    settings = "os", "compiler", "build_type", "arch"
    homepage = "https://github.com/ulfjack/ryu.git"

    def source(self):
        git = scm.Git(self, folder="..")
        git.clone("https://github.com/ulfjack/ryu.git", target="src")
        git = scm.Git(self, folder=self.source_folder)
        # no release tag, use master
        commit = "1264a94"
        git.checkout(commit)
        apply_conandata_patches(self)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        build_env = VirtualBuildEnv(self)
        build_env.generate()
        run_env = VirtualRunEnv(self)
        run_env.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_CXX_FLAGS"] = " -fPIC "
        tc.cache_variables["CMAKE_C_FLAGS"] = " -fPIC "
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def package(self):
        copy(
            self,
            "LICENSE*",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ryu")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_target_name", "ryu::ryu")

        self.cpp_info.components["libryu"].set_property("pkg_config_name", "ryu")
        self.cpp_info.components["libryu"].libs = ["ryu"]

        if not is_msvc:
            self.cpp_info.components["generic_128"].set_property(
                "pkg_config_name", "generic_128"
            )
            self.cpp_info.components["generic_128"].libs = ["generic_128"]
