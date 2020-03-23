# This setup script is partly based on the 'cmake_example' of
# Pybind, found at: https://github.com/pybind

# Here is the accompanying LICENSE text, which has to be included:

# Copyright (c) 2016 The Pybind Development Team, All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# You are under no obligation whatsoever to provide any bug fixes, patches, or
# upgrades to the features, functionality or performance of the source code
# ("Enhancements") to anyone; however, if you choose to make your Enhancements
# available either publicly, or directly to the author of this software, without
# imposing a separate written license agreement for such Enhancements, then you
# hereby grant the following license: a non-exclusive, royalty-free perpetual
# license to install, use, modify, prepare derivative works, incorporate into
# other computer software, distribute, and sublicense such enhancements or
# derivative works thereof, in binary and source code form.

import os
import re
import sys
import platform
import subprocess
import inspect

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
from distutils.version import LooseVersion

my_dir = os.path.abspath(os.path.dirname(__file__))
my_build_dir = os.path.join(my_dir, 'build')
my_package_dir = os.path.join(my_build_dir, 'qisa_as')

# These global variables are needed because there is no easy way to tell which
# command is used to build the qisa-as package.

_build_ext_is_called_by_develop = False
_build_ext_is_called_by_install = False
_install_dir_for_build_ext = None

class CMakeExtension(Extension):
  def __init__(self, name, sourcedir=''):
    Extension.__init__(self, name, sources=[])
    self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
  def run(self):
    try:
      out = subprocess.check_output(['cmake', '--version'])
    except OSError:
      raise RuntimeError("CMake must be installed to build the following extensions: " +
                         ", ".join(e.name for e in self.extensions))

    if platform.system() == "Windows":
      cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
      if cmake_version < '3.1.0':
        raise RuntimeError("CMake >= 3.1.0 is required on Windows")

    for ext in self.extensions:
      self.build_extension(ext)

  def build_extension(self, ext):
    develop_flag_file = os.path.abspath(os.path.join(self.build_temp, '_qisa_as_built_for_develop.txt'))
    install_flag_file = os.path.abspath(os.path.join(self.build_temp, '_qisa_as_built_for_install.txt'))

    extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

    if not os.path.exists(self.build_temp):
      os.makedirs(self.build_temp)

    if _build_ext_is_called_by_develop:
      if os.path.isfile(install_flag_file):
        raise RuntimeError("Existing build directory is built for the setuptools 'install' "
                           "command and cannot be used with the 'develop' command!\n"
                           "Please remove the build directory '{}' "
                           "before trying again.".format(os.path.abspath(my_build_dir)))
      # Create the 'flag' file used to detect build type mismatches.
      if not os.path.isfile(develop_flag_file):
        with open(develop_flag_file, 'w'):
          pass

      installdir = my_package_dir
      staging_dir = os.path.abspath(my_package_dir)
    elif _build_ext_is_called_by_install:
      if os.path.isfile(develop_flag_file):
        raise RuntimeError("Existing build directory is built for the setuptools 'develop' "
                           "command and cannot be used with the 'install' command!\n"
                           "Please remove the build directory '{}' "
                           "before trying again.".format(os.path.abspath(my_build_dir)))
      installdir = _install_dir_for_build_ext
      staging_dir = os.path.abspath(os.path.join(self.build_lib, 'qisa_as'))

      # Create the 'flag' file used to detect build type mismatches.
      if not os.path.isfile(install_flag_file):
        with open(install_flag_file, 'w'):
          pass
    else:
      raise RunTimeError('Setup.py can only be called using \'develop\' or \'install\' commands.')

    installdir = os.path.abspath(installdir)

    cfg = 'Debug' if self.debug else 'Release'

    cmake_args = ['-DCMAKE_BUILD_TYPE=' + cfg,
                  '-DCMAKE_INSTALL_PREFIX=' + staging_dir,
                  '-DCMAKE_INSTALL_RPATH=' + installdir,
                  '-DPYTHON_EXECUTABLE=' + sys.executable,
                  '-DQISA_AS_INSTALL_FOR_SETUP_PY=1']

    build_args = ['--config', cfg]

    if platform.system() == "Windows":
      cmake_args += ['-G', 'NMake Makefiles']
    else:
      build_args += ['--', '-j4']

    env = os.environ.copy()
    env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                          self.distribution.get_version())
    subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
    subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
    subprocess.check_call(['cmake', '--build', '.', '--target', 'install'], cwd=self.build_temp)


class CMakeInstall(_install):
  def run(self):
    global _build_ext_is_called_by_develop
    global _build_ext_is_called_by_install
    global _install_dir_for_build_ext
    _build_ext_is_called_by_develop = False
    _build_ext_is_called_by_install = True
    # For linux: the RPATH must point to where the qisa-as package will be installed.
    _install_dir_for_build_ext = os.path.join(self.install_lib, 'qisa_as')
    _install.run(self)

class CMakeDevelop(_develop):
  def run(self):
    global _build_ext_is_called_by_develop
    global _build_ext_is_called_by_install
    _build_ext_is_called_by_develop = True
    _build_ext_is_called_by_install = False
    _develop.run(self)

def get_version(verbose=0):
  """ Extract version information from source code """

  matcher = re.compile('[\t ]*#define[\t ]+QISA_(MAJOR|MINOR|PATCH)_VERSION[\t ]+(.*)')

  qisa_major_version = None
  qisa_minor_version = None
  qisa_patch_version = None

  try:
    with open(os.path.join(my_dir, 'qisa_version.h'), 'r') as f:
      for ln in f:
        m = matcher.match(ln)
        if m:
          version_val = int(m.group(2))
          if m.group(1) == 'MAJOR':
            qisa_major_version = version_val
          elif m.group(1) == 'MINOR':
            qisa_minor_version = version_val
          else:
            qisa_patch_version = version_val

            if ((qisa_major_version is not None) and
                (qisa_minor_version is not None) and
                (qisa_patch_version is not None)):
              version = '{}.{}.{}'.format(qisa_major_version,
                                          qisa_minor_version,
                                          qisa_patch_version)
              break;
  except Exception as E:
    print(E)
    version = 'none'
  if verbose:
    print('get_version: %s' % version)
  return version

def readme():
  with open(os.path.join(my_dir, 'README.md')) as f:
    return f.read()

def license():
  with open(os.path.join(my_dir, 'LICENSE')) as f:
    return f.read()

# Create the build directory and the place where the package will be found
# once build is complete.
os.makedirs(my_package_dir, exist_ok=True)

# Create the __init__.py file that imports the required classes.
with open(os.path.join(my_package_dir, '__init__.py'), 'w') as init_file:
  print('from .pyQisaAs import QISA_Driver, qisa_qmap', file=init_file)

# Make sure that we are running from 'this' directory, otherwise
# 'setup()' cannot find the 'build' directory.
os.chdir(my_dir)


# Now perform the actual setup.
setup(name='QISA_AS',
      version=get_version(),
      use_2to3=False,
      author='Vincent Newsum',
      author_email='vincent.newsum@tno.nl',
      maintainer='Vincent Newsum',
      maintainer_email='vincent.newsum@tno.nl',
      description=('Assembler/Disassembler for the Quantum Instruction Set Architecture (QISA), '
                   'which is part of QuTech\'s ElecPrj_CCLight.'),
      long_description=readme(),
      url='https://github.com/DiCarloLab-Delft/ElecPrj_CCLight/qisa-as',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Assemblers',
        'Topic :: Software Development :: Disassemblers'
      ],
      license=license(),
      ext_modules=[CMakeExtension('qisa_as')],
      cmdclass=dict(build_ext=CMakeBuild, install=CMakeInstall, develop=CMakeDevelop),
      zip_safe=False,
      packages=['qisa_as'],
      package_dir={'': 'build'}
)
