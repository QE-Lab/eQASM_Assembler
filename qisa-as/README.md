## _QISA-AS_: Assembler/Disassembler for the Quantum Instruction Set Architecture

### Introduction
As part of project
[ElecPrj_CCLight](https://github.com/DiCarloLab-Delft/ElecPrj_CCLight),
_QISA-AS_ is mainly used to assemble source code that is given in the Quantum
Instruction Set Architecture (QISA).

It can also be used to disassemble generated code, in order to examine
existing QISA code in binary form.

QISA instructions can be divided into two groups:

- Classic instructions that are used for the usual arithmetic, testing and
branching. These instructions are also termed as *Single Instruction
Format* instructions due to the fact that these instructions are encoded
into a single binary instruction word.

- Quantum instructions that are used for performing quantum operations.
These instructions are also termed as *Double Instruction Format*
instructions due to the fact that two of these instructions can be encoded
into a single binary instruction word.

One of the main features of _QISA-AS_, is its flexibility of the instruction
set.
The classic instructions are fixed in name, functionality and syntax, but
their opcodes can be specified at build time.

The quantum instructions benefit from even more flexibility: the number of
instructions and their opcodes can be *configured*, not only at build time,
but at *runtime* as well.

Another way of flexibility is how the _QISA-AS_ assembler/disassembler can be
invoked:

- From the command-line, by using the `qisa-as` executable.
- From Python: by using the supplied python interface library
  `pyQisaAs.py`.

The syntax of the instructions that are supported by _QISA-AS_ are
described in [README-SYNTAX.md](README-SYNTAX.md)

The early versions of the _QISA-AS_ assembler were based on ideas from:
- https://github.com/jonathan-beard/simple_wc_example
- https://github.com/optixx/mycpu

The next sections cover:
- The invocation of the _QISA-AS_ assembler/disassembler.
- How to build _QISA-AS_, on Linux and on Microsoft Windows.

### Invocation of _QISA-AS_

#### Command line
The _QISA-AS_ Assembler/Disassembler can be invoked by running the `qisa-as`
executable.

Specifying option `-h` or `--help` gives the following help message:

---
```
Usage: qisa-as [OPTIONS] INPUT_FILE
Assembler/Disassembler for the Quantum Instuction Set Architecture (QISA).

Options:
  -q QMAP_FILE      Load quantum instructions from given QMAP_FILE.
  --dumpspecs       Output the opcode specifications that have been configured into the assembler
  -d[ 1 | 2 ]       Disassemble the given INPUT_FILE
                    Extra integer option suffix specifies the disassembly output format, default = 1
  -o OUTPUT_FILE    Save binary assembled or textual disassembled instructions to the given OUTPUT_FILE
  -t                Enable scanner and parser tracing while assembling
  -V, --version     Show the program version and exit
  -v, --verbose     Show informational messages while assembling
  -h, --help        Show this help message and exit

Note:
  If option -q is not given, an attempt is made to load the quantum instructions from
  the file specified in the environment variable QISA_AS_QMAP_FILE.
  If -q is not given and QISA_AS_QMAP_FILE is not defined, the factory default quantum instruction
  set will be used instead.
```
---

Some of the available options warrant more in-depth descriptions:

<a name="cmdline-q_option"/>

- `-q QMAP_FILE`<br>
  This is the way to load new quantum instructions into _QISA-AS_.
  The quantum instruction definitions are specified using the following format:

  * `def_q_arg_none['<instruction_name>'] = <opcode>`
    This specifies a quantum instruction that does not have an argument.

  * `def_q_arg_st['<instruction_name>'] = <opcode>`
    This specifies a quantum instruction that expects an s-register argument.

  * `def_q_arg_tt['<instruction_name>'] = <opcode>`
    This specifies the quantum instructions that expect a t-register argument.

  At build-time, _QISA-AS_ is configured with a default instruction set,
  using a file consisting of this same format, but in that file, the
  opcodes for the classic, single format instructions are also specified
  using the following format:

    `def_opcode['<instruction_name>'] = <opcode>`

  _QISA-AS_ still recognizes lines that conform to this format, but will
  silently ignore them.  This is done so that a previously dumped
  instruction specification (See
  [`--dumpspecs`](#cmdline-dumpspecs_option)), can be used as input map
  file for the `-q` option.

<a name="cmdline-dumpspecs_option"/>

- `--dumpspecs`<br>
  This outputs the instruction specifications that have been configured
  into the assembler. The format with which this is given is the same as
  described at the item about the `-q` option.
  In principle, you could capture the output of this option to a file,
  modify it as you like, and load this file as new quantum instruction set
  using the `-q` option.

<a name="cmdline-d_option"/>

- `-d[ 1 | 2 ]`<br>
  This invokes the disassembler instead of the assembler.
  The input file is assumed to contain previously assembled QISA
  instructions in binary form.
  The disassembler decodes these instructions and outputs the represented
  assembler source code.
  Note that the assembler will only produce disassembled instructions
  according to the _low-level_ assembly (See
  [README-SYNTAX.md](README-SYNTAX.md)).

  An extra integer suffix can be specified after the -d option, which selects the
  disassembly output format.
  Currently, two disassembly output formats are defined:

    * 1:
      Instruction hex code in front, decoded instruction as comment, as in:

      `29600002   # label_0: FBR EQ, R22`


      This is the default disassembly output format (if no suffix is
      specified after the `-d` option.

    * 2:
      Decoded instruction in front, instruction hex code as comment, as in:

      `label_0: FBR EQ, R22   # 0x29600002`

  >NOTE: If specified, there should be no space between the `-d` option and
  >the integer suffix.

- `-t`<br>
  This is a debugging aid that can be used during development of this
  assembler.
  It turns on debugging output that helps to understand assembly grammar
  and syntax specification errors.

#### Python

_QISA-AS_ can also be invoked from a Python interpreter.

For this purpose, the _QISA-AS Python Interface Library_ (`qisa_as`
package) is provided.

Two Python types are defined in this interface library:

* `QISA_Driver`<br>
  This contains Python wrapper code that interfaces with _QISA-AS_.

* `qisa_qmap`<br>
  This defines the type used to convert Python dictionaries into something
  understood by _QISA-AS_.

The QISA-AS Python Interface Library package (`qisa_as`) must be imported into Python
like this:

```python
from qisa_as import QISA_Driver, qisa_qmap
```

> Note:
> This assumes installation of the QISA-AS Python Interface Library using
> 'setup.py' as described in a later section.

After that, an instance of `QISA_Driver` must be created in order to be able
to use _QISA-AS_.
This is a code example:

```python
driver = QISA_Driver()
```

A complete example can be found in directory 'test\_python\_interface'

```
Note that only version '3.x' of the Python interpreter is supported.
```

The following functions are available in `QISA_Driver` (listed in
alphapetical order):

```
Note: some functions return a boolean result, which is True on succes, and
False on failure. In case of failure, the function `getLastErrorMessage()`
can be used to get more detailed information about the failure.
```

- `bool assemble(filename:str)`<br>
  Assemble the given file, which is assumed to contain QISA assembly source
  code.

- `bool disassemble(filename:str)`<br>
  Disassembles the given file, which is assumed to contain QISA
  instructions in binary form.

- `str dumpInstructionsSpecification()`<br>
  Retrieves the currently configured QISA instructions specification as a
  multi-line string.

- `enableParserTracing(enabled:bool)`<br>
  This is a debugging aid that can be used during development of this
  assembler.
  When enabled is True, this turns on debugging output that helps to
  understand assembly grammar specification errors.

- `enableScannerTracing(enabled:bool)`<br>
  This is a debugging aid that can be used during development of this
  assembler.
  When enabled is True, this turns on debugging output that helps to
  understand assembly syntax specification errors.

- `bool setDisassemblyFormat(int format_id)`<br>
  Set the disassembly format to one of the known format types.
  See the [`-d` command line option](#cmdline-d_option) for a description
  of the disassembly output formats.

- `str getDisassemblyOutput()`<br>
  Normally, this is used after having called the `disassemble()` function.
  If disassembly was successful (return value was `True`),
  `getDisassemblyOutput()` can be used to retrieve the disassembly output
  as a multi-line string.

- `tuple(str) getInstructionsAsHexStrings(withBinaryOutput:bool)`<br>
  This function can be called to examine the results of a successful
  assembly (using the `assemble()` function).
  It returns the generated code as a list (tuple) of strings that contain the
  hexadecimal values of the encoded instructions, one instruction per tuple
  element.
  If withBinaryOutput is True, the binary representation of the instructions
  will be added adjacent to the hexadecimal values.

- `str getLastErrorMessage()`<br>
  Some functions return a boolean result, which is True on succes and False
  on failure. In case of failure, `getLastErrorMessage()` can be used to
  get more detailed information about the failure.

- `str getVersion()`<br>
  Return a string that represents the version of _QISA-AS_.
  Note that this is a static function, which can be called without
  instantiating an instance of `QISA_Driver`.
  The following example demonstrates this:

  ```python
  print ("QISA_AS Version: ", QISA_Driver.getVersion())
  ```
<a name="python-load_q_dicts"/>

- `bool loadQuantumInstructions(arg_none_map:qisa_qmap,
  arg_st_map:qisa_qmap, arg_tt_map:qisa_qmap)`<br>
  Load the quantum instructions that have been specified in the given maps
  into _QISA-AS_.

  Description of the parameters:

    * `arg_none_map`: Specifies quantum instructions that do not have an argument.
    * `arg_st_map`:  Specifies quantum instructions that expect an s-register argument.
    * `arg_tt_map`:  Specifies quantum instructions that expect a t-register argument.

    A note about the `qisa_map` type:
    This is a special type that is used to convert a python dictionary to
    something that _QISA-AS_ can understand.

    The way to call this function is as follows:

    ```python
    success = driver.loadQuantumInstructions(qisa_qmap(arg_none_dict),
                                             qisa_qmap(arg_st_dict),
                                             qisa_qmap(arg_tt_dict))
    ```

    Where `arg_none_dict`, `arg_st_dict` and `arg_tt_dict` are Python
    dictionaries that contain the mapping of instruction names to their
    opcodes.

<a name="python-load_q_file"/>

- `bool loadQuantumInstructions(qmapFilename:str)`<br>
  Parse the contents of the given file that contains quantum instruction
  specifications.
  See the [`-q` command line option](#cmdline-q_option) for a description
  of the required format of the given file.

- `reset()`
  Free the resources allocated by QISA_Driver and reset it, such that it
  can be used for assembly/disassembly again.
  >NOTE: A reset() is done implicitly at each call to
  >assemble()/disassemble().

- `bool save(outputFilename:str)`<br>
  Save binary assembled or textual disassembled instructions to the given
  output file.

- `setVerbose(verbose:bool)`<br>
  This determines whether or not informational messages are shown while the
  assembler decodes its input instructions.
  Set `verbose` to True to enable this.


If you type `help(driver)` the available functions will be described.

### Building _QISA-AS_

#### Dependencies

In order to build this assembler, you need CMake, bison, flex, and a C++
compiler that supports C++11.

A python interface is also provided: This necessitates swig and the python
development environment.

##### Linux

The Linux distribution on which this software has been tested on Ubuntu,
both version 16.04 as well as version 17.04.
The following software packages are needed:

| Package       | Description                                        |
| ------------- | -------------------------------------------------- |
| `bison`       | Context-free grammar parser generator              |
| `cmake`       | Cross-platform build tool                          |
| `flex`        | Lexical analyser generator                         |
| `g++-5`       | C++ compiler that supports C++11                   |
| `python3`     | Interpreter for the Python language, version 3.x   |
| `python3-dev` | Development headers and libraries for `python3`    |
| `swig`        | Tool used to call C++ functions from Python        |

These packages can be installed using the following command line:
`sudo apt-get install bison cmake flex g++-5 python3 python3-dev swig`

##### Windows

CMake can be installed from: https://cmake.org/download
You can use either the Windows win64-x64 or the win32-x86 installer, depending
on your Windows installation.

###### Bison & Flex
For Bison and flex, you can install the latest win\_flex\_bison package from
https://sourceforge.net/projects/winflexbison/files
It is distributed as a zip archive, which must be unpacked in a separate
directory.
Add that directory to your Windows PATH variable.

> __IMPORTANT__:
>
> Be sure to download the latest win_flex_bison __*2.5.x*__ version that includes Bison version 3.x!
>
> Do __NOT__ use the _2.4.x_ version!

The version that is known to work for _QISA-AS_ is `2.5.10`.

###### C++

For C++, you can install Visual Studio 2017 Community Edition
(https://www.visualstudio.com/thank-you-downloading-visual-studio/?sku=Community&rel=15#).

###### Python
Python can be retrieved from https://www.python.org/downloads/windows/

You need to get the latest 'Windows x86-64 executable installer'

If you want, there is a nice tutorial that might help if you need more
information:
https://www.howtogeek.com/197947/how-to-install-python-on-windows/

In order for this Python installation to be picked up by cmake, you need to
define two environment variables:

- PYTHON_LIBRARY             - path to the python library
- PYTHON_INCLUDE_DIR         - path to where Python.h is found

Example using Python 3.6.1:
```
PYTHON_INCLUDE: C:\Python36\include
PYTHON_LIB: C:\Python36\libs\python36.lib
```

###### SWIG

SWIG is used to provide the python interface to the QISA assembler.
It can be downloaded from:
https://sourceforge.net/projects/swig/files/swigwin/

Take the latest version.

SWIG for Windows is distributed as a zip archive, which must be unpacked in a
separate directory.
Add that directory to your Windows PATH variable.

#### Building the complete QISA-AS release.

CMake is used to generate the platform specific Makefile/Solution file with
which the `qisa-as` executable can be built.
The QISA-AS Python Interface Library is also built, but see the section about using
`setup.py` if you intend to use only the QISA-AS Python Interface Library.

##### Linux

Create a directory 'build' in this directory.
From within that directory, invoke CMake and then make.
In commands:

```
$ mkdir build
$ cd build
$ cmake ..
$ make
```

The `qisa-as` executable can be found in this directory afterwards.

Built and tested on Ubuntu 16.04.

##### Windows (Using Visual Studio IDE)

* Create an out-of-source 'build' directory. (A directory outside of <CCLight root>/qisa-as).
* Start up 'CMake-gui'
* Using the 'Browse Source...' button, locate the directory <CCLight root>/qisa-as.
* Using the 'Browse Build...' button, locate the 'build' directory that has just
  been created.
* Now press on the 'Configure' button.
  There will be a dialog in which you can specify the kind of CMake generator to use.
  For the tested case, Visual Studio 15 2017 was used, along with the option to
  use default native compilers.
* Now press the 'Generate' button.

This should have generated a (in case of 'Visual Studio 15 2017') solution in
the chosen 'build' directory, named 'qisa-as.sln'.

* Open the generated 'qisa-as.sln' using Visual Studio 15 2017
* Select the 'Solution configuration' you want (By default, this is Debug, but
  you might want to select 'Release' instead).
* Press 'F7' to build the solution.

The 'qisa-as.exe' executable can be found in the 'build/Release' directory after
the compilation has terminated.
> Note that 'qisa-as.exe' depends on the shared library 'qisa-as-lib.dll', which must be installed in the same directory as 'qisa-as.exe'.

Built and tested on Windows 10.

##### Windows (Using Powershell)

* Create an out-of-source 'build' directory. (A directory outside of
  <CCLight root>/qisa-as).
* Start up Powershell and go to that directory.
* `cmake -G "NMake Makefiles" <CCLight root>/qisa-as`
* `nmake`

> Note: This is a debug build by default...

The 'qisa-as.exe' executable can be found in the 'build' directory after the
compilation has terminated.

> Note that 'qisa-as.exe' depends on the shared library 'qisa-as-lib.dll', which must be installed in the same directory as 'qisa-as.exe'.

Built and tested on Windows 10.


#### Building and installing the QISA-AS Python Interface using setup.py.

In order to facilitate operating QISA-AS using Python, a setuptools
`setup.py` script is provided.
This basically automates the steps described above, and additionally
installs the QISA-AS Python Interface Library as a separate package named `qisa_as`.
The qisa-as executable however, is not installed, as it is assumed that
only the Python interface will be used.

Invoking `setup.py` is relatively straightforward and can be done
irrespective of the platform (Linux or Windows):

> NOTE: Only Python version 3 is supported, so Linux users might have to
> use the 'python3' command to invoke python, in case both versions are installed.

```
python setup.py {develop|install} [--user]
```
 * The `install` command will build the QISA-AS Python Interface Library
   and install a copy of the intermediate `qisa_as` package in Python's
   deployment directory (usually a directory called `site-packages`).


 * The `develop` command will build the QISA-AS Python Interface Library
   but keep the intermediate `qisa_as` package within the *'build'*
   directory and only create a reference to that package Python's
   deployment directory.

 * The `--user` option instructs `setup.py` to use Python's per-user
   deployment directory that can for example be used when the user doesn't
   have administrative rights to install the package in Python's main deployment
   directory.

#### Testing

In directory 'qisa\_test\_assembly', you can find some assembly source files that
you can use to test the generated assembler.
The file 'test\_assembly.qisa' contains all known 'classic' instructions and aliases,
and some quantum instructions.


#### Python interface

The provided python interface is generated using SWIG.
In the section about the [Python Library Interface](#python) you can see
which functions are provided.

In order to use the python interface from another location than the <build_dir>,
you will have to copy some files from there to the chosen installation
directory.

These are:
##### Linux
* libqisa-as-lib.so
* _pyQisaAs.so
* pyQisaAs.py

##### Windows
* qisa-as-lib.dll
* _pyQisaAs.pyd
* pyQisaAs.py

In the directory 'test\_python\_interface' you can find an example python
script that shows how to assemble a QISA assembly file, and disassemble the
generated binary assembly file afterwards.

A README.md file describes how you might run it.

#### Implementation notes

Flexibility has been the focus of the current _QISA-AS_ implementation.
This is because the opcodes of the classic instructions are not yet final.
Also, the quantum instructions themselves are not fully specified and are
subject to change.

The solution found is to have the specification of the opcodes of the
classic instructions and that of the quantum instructions (instruction and
opcode) into a text file (`qisa_opcodes.qmap`).
This file is processed during build time, and generates a C++ file that is
used to incoprporate the instructions and their opcodes into _QISA-AS_.
See the [`-q` command line option](#cmdline-q_option) for a description of
the required format of `qisa_opcodes.qmap`. The file itself also contains
an extensive description of the file format.

Note that the quantum instructions that are defined in `qisa_opcodes.qmap`
form the default set of quantum instructions. They can be overridden using
the [`-q` command line option](#cmdline-q_option) or the Python interface
functions
[loadQuantumInstructions(arg_none_map, arg_st_map, arg_tt_map)](#python-load_q_dicts)
and [bool loadQuantumInstructions(qmapFilename:str)](#python-load_q_file).
