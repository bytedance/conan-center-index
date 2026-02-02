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
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import (
    apply_conandata_patches,
    export_conandata_patches,
    get,
    copy,
)
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools import scm
import os
import re

required_conan_version = ">=1.53.0"


class SonicCppConan(ConanFile):
    name = "sonic-cpp"
    description = (
        "A fast JSON serializing & deserializing library, accelerated by SIMD."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bytedance/sonic-cpp"
    topics = ("json", "parser", "writer", "serializer", "deserializer", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
        }

    def requirements(self):
        cppstd = self.settings.get_safe("compiler.cppstd")
        # Assume we would need it if not told otherwise
        if not cppstd or cppstd < "17":
            self.requires("string-view-lite/1.7.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        supported_archs = ["x86", "x86_64"]
        supported_archs.extend(["armv8", "armv8.3", "armv9"])

        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support MSVC now.")

    def source(self):
        sonic_version_pattern = r"0\.\d\.\d+"
        if re.findall(sonic_version_pattern, self.version):
            git = scm.Git(self, folder="..")
            git.clone(self.conan_data["sources"][self.version]["url"], target="src")
            git = scm.Git(self, folder=self.source_folder)
            commit = self.conan_data["sources"][self.version]["revision"]
            git.checkout(commit)
        else:
            get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            if self.settings.arch in ["x86", "x86_64"]:
                self.cpp_info.cxxflags.extend(["-mavx2", "-mpclmul"])
