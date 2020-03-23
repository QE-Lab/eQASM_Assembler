%begin %{
#ifdef _MSC_VER
#define SWIG_PYTHON_INTERPRETER_NO_DEBUG
#endif
%}

%module pyQisaAs
%{
#include "qisa_driver.h"
%}

%include std_string.i
using std::string;

%include std_vector.i
namespace std {
   %template(StringVector) vector<string>;
};

%include std_map.i
namespace std {
   %template(qisa_qmap) map<string, int>;
};

namespace QISA
{

class QISA_Driver
{
public:

  %feature("autodoc", "Constructor");
  QISA_Driver();

  %feature("autodoc");
  virtual ~QISA_Driver();

  %feature("autodoc");
  void read(std::string input_filename);

  %feature("autodoc", "
Return a string that represents the version of the assembler.
");
  static std::string getVersion();

  %feature("autodoc", "
Enable or disable scanner (flex) tracing.
This is a debugging aid that can be used during development of this assembler.

Parameters
----------
enabled  -- True if scanner tracing should be enabled, False if it should be disabled.
");
  void enableScannerTracing(bool enabled);

  %feature("autodoc", "
Enable or disable parser (bison) tracing.
This is a debugging aid that can be used during development of this assembler.

Parameters
----------
enabled: bool  -- True if parser tracing should be enabled, False if it should be disabled.
");
  void enableParserTracing(bool enabled);

  %feature("autodoc", "
Assemble the given file.

Parameters
----------
filename: str File that contains QISA assembly source code.

Returns
-------
--> bool: True on success, false on failure.

Note
----
On error, you can use getLastErrorMessage() to get a description of that error.
");
  bool assemble(const std::string& filename);

%feature("autodoc", "
Disassemble the given file.

Parameters
----------
filename: str File that contains QISA instructions in binary form.

Returns
-------
--> bool: True on success, false on failure.
");
  bool disassemble(const std::string& filename);

  %feature("autodoc", "
Returns
-------
--> str: The last generated error message.
");
  std::string getLastErrorMessage();

  %feature("autodoc", "
Change the verbosity of the assembler.
This determines whether or not informational messages are shown while the assembler decodes its input instructions.

Parameters
----------
verbose: bool  -- Specifies the verbosity of the assembler.

");
  void setVerbose(bool verbose);

  %feature("autodoc", "
Retrieve the generated code as a list of strings that contain the hex values of the encoded instructions.

Parameters
----------
withBinaryOutput: bool  -- If True, the binary representation of the instruction will be appended to the hex codes.

Returns
-------
--> tuple of str: The generated instructions, one encoded instruction per element.
");
  std::vector<std::string>
  getInstructionsAsHexStrings(bool withBinaryOutput);

%feature("autodoc", "
Set the disassembly format to one of the known format types.

The known formats:

  1: Instruction hex code in front, decoded instruction as comment, as in:

         29600002   # label_0: FBR EQ, R22

     This is the default disassembly output format.

  2: Decoded instruction in front, instruction hex code as comment, as in:

         label_0: FBR EQ, R22   # 0x29600002

Parameters
----------
format_id: int Sets the output format in which the disassembly must be given.

Returns
-------
--> bool: True on success, false on failure.

");
  bool setDisassemblyFormat(int format_id);

%feature("autodoc", "
Retrieve the disassembly output as a multi-line string.

Returns
-------
--> str: The disassembly output: one (or more, in case of quantum) disassembled instruction per line.
");
  std::string getDisassemblyOutput();


  %feature("autodoc", "
Save binary assembled or textual disassembled instructions to the given output file.

Parameters
----------
outputFileName: str  -- Name of the file in which to store the generated output.
");
  bool save(const std::string& outputFileName);


%feature("autodoc", "
Retrieve the configured QISA instruction specifications as a multi-line string.

Returns
-------
--> str: The configured QISA opcode specification.
");
  std::string dumpInstructionsSpecification();

  %feature("autodoc", "
Free the resources allocated by QISA_Driver and reset it, such that it can be used for assembly/disassembly again.
NOTE: A reset() is done implicitly at each call to assemble()/disassemble().
");
  void reset();

  %feature("autodoc", "
Parse the contents of the given file that contains quantum instruction specifications.
The quantum instruction definitions are specified using the following format:

   def_q_arg_none['<instruction_name>'] = <opcode>
   This specifies the quantum instructions that do not have an argument.

   def_q_arg_st['<instruction_name>'] = <opcode>
   This specifies the quantum instructions that expect an s-register argument.

   def_q_arg_tt['<instruction_name>'] = <opcode>
   This specifies the quantum instructions that expect a t-register argument.

Parameters
----------
qMapFilename: str File that specifies quantum instructions.

Returns
-------
--> bool: True on success, false on failure.

Note
----
On error, you can use getLastErrorMessage() to get a description of that error.
");
  bool loadQuantumInstructions(const std::string& qMapFilename);

  %feature("autodoc", "
Load the quantum instructions that have been specified in the given maps into qisa-as.

Parameters
----------
arg_none_map: qisa_qmap Specifies quantum instructions that do not have an argument.
arg_st_map:   qisa_qmap Specifies quantum instructions that expect an s-register argument.
arg_tt_map:   qisa_qmap Specifies quantum instructions that expect a t-register argument.

Returns
-------
--> bool: True if the instructions were accepted, False if they
          contain errors, such as duplicate opcodes.

Note
----
On error, you can use getLastErrorMessage() to get a description of that error.
");
  bool
  loadQuantumInstructions(const std::map<std::string, int>& arg_none_map,
                         const std::map<std::string, int>& arg_st_map,
                         const std::map<std::string, int>& arg_tt_map);


};

}
