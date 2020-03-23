#pragma once

#include <string>
#include <cstddef>
#include <istream>
#include <sstream>
#include <map>
#include <set>
#include <algorithm>
#include <regex>

namespace QISA
{

/**
 * This class is used to parse a qisa '.qmap' file that contains
 * quantum instruction definitions.
 *
 * The quantum instruction definitions are specified using the following format:
 *
 *   def_q_arg_none['<instruction_name>'] = <opcode>
 *   This specifies the quantum instructions that do not have an argument.
 *
 *   def_q_arg_st['<instruction_name>'] = <opcode>
 *   This specifies the quantum instructions that expect an s-register argument.
 *
 *   def_q_arg_tt['<instruction_name>'] = <opcode>
 *   This specifies the quantum instructions that expect a t-register argument.
 *
 * At build-time, qisa-as is configured with a default instruction set, using a
 * file consisting of this same format, but in that file, the opcodes for the
 * classic, single format instructions are also specified using the following
 * format:
 *
 *   def_opcode['<instruction_name>'] = <opcode>
 *
 * The parser still recognizes lines that conform to this format,
 * but will silently ignore them.
 * This is done so that a previously dumped opcode specification (using
 * QISA_Driver's dumpOpcodeSpecification() function), can be modified and
 * used as input file without having to remove the def_opcode specifiations
 * first.
 */
class QISA_QMapParser
{
public:

  typedef std::map<std::string, int> q_map_t;

  /**
   * Constructor.
   */
  QISA_QMapParser();

  /**
   * Destructor.
   */
  virtual
  ~QISA_QMapParser()
  {}

  /**
   * Reset the parser such that it can be used to parse a new file again.
   *
   * @note
   *   A reset() is done implicitly at each call to parse().
   */
  void
  reset();

  /**
   * Parse the given file that contains quantum instruction specifications.
   * @param filename File to parse.
   *
   * @return True on success, false if an error was detected during parse.
   *
   * @note
   *   On error, you can use getLastErrorMessage() to get a
   *   description of that error.
   */
  bool
  parse(const std::string& filename);

  /**
   * @return The last generated error message.
   */
  std::string
  getLastErrorMessage();

  /**
   * Get the instruction code maps that previously have been parsed from file.
   *
   * @param[out] arg_none_map Instruction code map for quantum
   *                          instructions without parameters.
   * @param[out] arg_st_map Instruction code map for quantum
   *                        instructions with an s-register parameter.
   * @param[out] arg_tt_map Instruction code map for quantum
   *                        instructions with a t-register parameter.
   *
   * @return True on success, false if previous parse results
   *         indicated an error occurred.
   *
   * @note
   *   On error, you can use getLastErrorMessage() to get a
   *   description of that error.
   */
  bool
  getInstructionCodeMaps(q_map_t& arg_none_map,
                         q_map_t& arg_st_map,
                         q_map_t& arg_tt_map);
private:

  /**
   * Clean up an input line by removing comments, leading and trailing
   * spaces and line endings.
   * The remaining characters are made lower case.
   *
   * @param inputLine String to be cleaned up.
   * @return Cleaned up string.
   */
  std::string
  cleanupLine(const std::string& inputLine);


  // Maximum value to specify as opcode.
  int _maxOpcodeVal;

  // Contains the opcodes for the quantum instructions that do not have an argument.
  q_map_t _q_inst_arg_none_opcodes;

  // Contains the opcodes for the quantum instructions specifying an st argument.
  q_map_t _q_inst_arg_st_opcodes;

  // Contains the opcodes for the quantum instructions specifying a tt argument.
  q_map_t _q_inst_arg_tt_opcodes;

  // Name of the file that has been parsed.
  std::string _filename;

  // Regular expression that is used for parsing map definitions.
  std::regex _mapEntryRegex;

  // Used to redirect error messages to.
  std::ostringstream _errorStream;

  // Records that an error occurred during a parse().
  bool _hadError;
};

} /* end namespace QISA */
