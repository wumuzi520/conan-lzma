#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class LZMAConan(ConanFile):
    name = "lzma"
    version = "5.2.3"
    description = "LZMA library is part of XZ Utils (a free general-purpose data compression software.)"
    url = "https://github.com/bincrafters/conan-lzma"
    license = "Public Domain"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    root = "xz-" + version
    install_dir = 'lzma-install'

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == 'Visual Studio':
            del self.options.fPIC

    def source(self):
        archive_name = "xz-%s.tar.gz" % self.version
        source_url = "https://tukaani.org/xz/%s" % archive_name
        tools.download(source_url, archive_name, verify=True)
        tools.untargz(archive_name)
        os.unlink(archive_name)

    def build_msvc(self):
        # windows\INSTALL-MSVC.txt
        with tools.chdir(os.path.join(self.root, 'windows')):
            target = 'liblzma_dll' if self.options.shared else 'liblzma'
            if str(self.settings.compiler.runtime).startswith('MT'):
                tools.replace_in_file('%s.vcxproj' % target,
                                      '<RuntimeLibrary>MultiThreadedDebugDLL</RuntimeLibrary>',
                                      '<RuntimeLibrary>MultiThreadedDebug</RuntimeLibrary>')
                tools.replace_in_file('%s.vcxproj' % target,
                                      '<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>',
                                      '<RuntimeLibrary>MultiThreaded</RuntimeLibrary>')
            command = tools.msvc_build_command(self.settings, 'xz_win.sln', targets=[target], upgrade_project=False)
            if self.settings.arch == 'x86':
                command = command.replace('/p:Platform="x86"', '/p:Platform="Win32"')
            self.run(command)

    def build_configure(self):
        prefix = os.path.abspath(self.install_dir)
        with tools.chdir(self.root):
            env_build = AutoToolsBuildEnvironment(self)
            args = ['--disable-xz',
                    '--disable-xzdec',
                    '--disable-lzmadec',
                    '--disable-lzmainfo',
                    '--disable-scripts',
                    '--disable-doc',
                    '--prefix=%s' % prefix]
            if self.options.fPIC:
                args.append('--with-pic')
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--enable-static', '--disable-shared'])
            if self.settings.build_type == 'Debug':
                args.append('--enable-debug')
            if str(self.settings.os) in ["Macos", "iOS", "watchOS", "tvOS"]:
                # disable host auto-detection, because configure fails to detect shared libraries support in that case
                env_build.configure(args=args, build=False, host=False, target=False)
            else:
                env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self.build_msvc()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="COPYING", dst="license", src=self.root)
        if self.settings.os == "Windows":
            inc_dir = os.path.join(self.root, 'src', 'liblzma', 'api')
            self.copy(pattern="*.h", dst="include", src=inc_dir, keep_path=True)
            arch = {'x86': 'Win32', 'x86_64': 'x64'}.get(str(self.settings.arch))
            target = 'liblzma_dll' if self.options.shared else 'liblzma'
            bin_dir = os.path.join(self.root, 'windows', str(self.settings.build_type), arch, target)
            self.copy(pattern="*.lib", dst="lib", src=bin_dir, keep_path=False)
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=bin_dir, keep_path=False)
        else:
            inc_dir = os.path.join(self.install_dir, 'include')
            lib_dir = os.path.join(self.install_dir, 'lib')
            self.copy(pattern="*.h", dst="include", src=inc_dir, keep_path=True)
            if str(self.settings.os) in ['Linux', 'Android']:
                if self.options.shared:
                    self.copy(pattern="*.so*", dst="lib", src=lib_dir, keep_path=False)
                else:
                    self.copy(pattern="*.a", dst="lib", src=lib_dir, keep_path=False)
            elif str(self.settings.os) in ['Macos', 'iOS', 'watchOS', 'tvOS']:
                if self.options.shared:
                    self.copy(pattern="*.dylib*", dst="lib", src=lib_dir, keep_path=False)
                else:
                    self.copy(pattern="*.a", dst="lib", src=lib_dir, keep_path=False)

    def package_info(self):
        if not self.options.shared:
            self.cpp_info.defines.append('LZMA_API_STATIC')
        self.cpp_info.libs = tools.collect_libs(self)
