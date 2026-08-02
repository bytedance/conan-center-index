from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv

import os

required_conan_version = ">=1.52.0"

class ProxygenConan(ConanFile):
    description = """ Proxygen """
    name = "proxygen"
    version = "2022.10.31.00"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def requirements(self):
        self.requires(f"wangle/{self.version}", headers=True, transitive_headers=True, transitive_libs=True)
        self.requires(f"folly/{self.version}", headers=True, transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.26.4]")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=False)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.shared:
            self.options["glib"].shared = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "16",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "17")

        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(self.name, self.settings.compiler))
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

        if self.settings.os in ["Macos", "Windows"]:
            raise ConanInvalidConfiguration("Not be tested on {} yet. ".format(self.settings.os))

    def layout(self):
        cmake_layout(self, build_folder='_build')

    def generate(self):
        build_env = VirtualBuildEnv(self)
        build_env.generate()

        run_env = VirtualRunEnv(self)
        run_env.generate()

        tc = CMakeToolchain(self, generator="Ninja")

        # https://gcc.gnu.org/onlinedocs/gcc-10.3.0/gcc/AArch64-Options.html
        if str(self.settings.arch) in ['armv8'] and not is_msvc(self):
            # SIMD neon & CRC hardware acceleration
            tc.variables["CMAKE_C_FLAGS"] = "-march=armv8.3-a"
            tc.variables["CMAKE_CXX_FLAGS"] = "-march=armv8.3-a"
        elif str(self.settings.arch) in ['armv9'] and not is_msvc(self):
            # gcc 12+ https://www.phoronix.com/news/GCC-12-ARMv9-march-armv9-a
            tc.variables["CMAKE_C_FLAGS"] = "-march=armv9-a"
            tc.variables["CMAKE_CXX_FLAGS"] = "-march=armv9-a"
        elif str(self.settings.arch) in ['x86', 'x86_64']:
            if not is_msvc(self):
                tc.variables["CMAKE_C_FLAGS"] = "-mfma -mavx2"
                tc.variables["CMAKE_CXX_FLAGS"] = "-mfma -mavx2"
            else:
                tc.variables["CMAKE_C_FLAGS"] = "/arch:FMA /arch:AVX2"

        tc.generate()

        CMakeDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        files.copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        files.copy(self, "README", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        files.copy(self, "CONTRIBUTING.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "proxygen")
        self.cpp_info.set_property("cmake_target_name", "proxygen::proxygen")

        self.cpp_info.components["proxygen"].libs = ["proxygen"]
        self.cpp_info.components["proxygen"].set_property("cmake_target_name", "proxygen::proxygen")

        self.cpp_info.components["proxygenhttpserver"].libs = ["proxygenhttpserver"]
        self.cpp_info.components["proxygenhttpserver"].requires = ["proxygen"]
        self.cpp_info.components["proxygenhttpserver"].set_property("cmake_target_name", "proxygen::proxygenhttpserver")

        self.cpp_info.components["proxygencurl"].libs = ["proxygencurl"]
        self.cpp_info.components["proxygencurl"].requires = ["proxygen"]
        self.cpp_info.components["proxygencurl"].set_property("cmake_target_name", "proxygen::proxygencurl")

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.components["proxygen"].names["cmake_find_package"] = "proxygen"
        self.cpp_info.components["proxygen"].names["cmake_find_package_multi"] = "proxygen"
        self.cpp_info.components["proxygenhttpserver"].names["cmake_find_package"] = "proxygenhttpserver"
        self.cpp_info.components["proxygenhttpserver"].names["cmake_find_package_multi"] = "proxygenhttpserver"
        self.cpp_info.components["proxygencurl"].names["cmake_find_package"] = "proxygencurl"
        self.cpp_info.components["proxygencurl"].names["cmake_find_package_multi"] = "proxygencurl"
