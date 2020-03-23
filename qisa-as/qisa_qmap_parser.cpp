#include <iostream>
#include <fstream>
#include <cstddef>
#include <sstream>
#include <algorithm>
#include <cctype>

#include <iomanip>

#include <qisa_qmap_parser.h>

namespace QISA
{

QISA_QMapParser::QISA_QMapParser()
  : _maxOpcodeVal(255) // Opcodes for quantum instructions are 8-bit wide.
  , _mapEntryRegex("^[ \\t]*"
                   "def_(opcode|q_arg_none|q_arg_st|q_arg_tt)"
                   "[ \\t]*\\[[ \\t]*"
                   "(['\\\"])(\\w+)\\2"
                   "[ \\t]*\\][ \\t]*"
                   "=[ \\t]*(0x[\\da-fA-f]+|-?\\d+)",
                   std::regex_constants::icase)
  , _hadError(-1)
{
  // Above regex should capture the definitions of the quantum
  // opcode maps in the following format:
  //
  //   def_q_arg_none['<instruction_name>'] = <opcode>
  //   def_q_arg_st['<instruction_name>'] = <opcode>
  //   def_q_arg_tt['<instruction_name>'] = <opcode>

  // The opcode can be given either in decimal or in hexadecimal
  // format (prefixed by '0x').
  //
  // Note that negative integers are accepted by this format, only
  // to be rejected when the value string is parsed.
  // This way, we can give a better error description.
}

void
QISA_QMapParser::reset()
{
  _q_inst_arg_none_opcodes.clear();
  _q_inst_arg_st_opcodes.clear();
  _q_inst_arg_tt_opcodes.clear();
  _filename.clear();
  _errorStream.str("");
  _errorStream.clear();
  _hadError = false;
}


std::string
QISA_QMapParser::cleanupLine(const std::string& inputLine)
{
  std::string result;

  bool had_nonspace = false;
  bool had_space = false;

  for(const char& ch : inputLine)
  {
    if (ch == '#')
    {
      // Ignore the rest of the input line and return the result.
      break;
    }
    else if ((ch == ' ') || (ch == '\t'))
    {
      if (!had_nonspace)
      {
        // Ignore leading spaces.
        continue;
      }
      if (!had_space)
      {
        result += ' ';
        had_space = true;
      }
      else if ((ch == '\n') || (ch == '\r'))
      {
        // Return result at EOL.
        break;;
      }
    }
    else
    {
      had_nonspace = true;
      had_space = false;
      result += tolower(ch);
    }
  }

  // Remove a possible remaining trailing space.
  if (!result.empty() && (result.back() == ' '))
  {
    result.pop_back();
  }

  return result;
}


bool
QISA_QMapParser::parse(const std::string& filename)
{
  reset();

  _filename = filename;

  // Contains the list of all opcodes. Used to check for duplicate opcodes.
  // The map maps an opcode to the line in the source file where it occurs, so
  // that a more useful error message can be given.
  std::map<int, int> usedOpcodes;


  // Contains the list of all instruction names. Used to check for duplicate names.
  // The map maps an instruction name to the line in the source file where
  // it is defined, so that a more useful error message can be given.
  std::map<std::string, int> usedInstructionNames;

  std::string line;
  size_t line_counter = 0;

  std::ifstream srcFile (_filename);
  if (srcFile.is_open())
  {
    while (std::getline(srcFile,line))
    {
      line_counter++;

      // Remove comments, leading, intermediate and trailing spaces.
      line = cleanupLine(line);

      if (line.empty())
      {
        // Empty line. next line please.
        continue;
      }

      // Now parse the line using a regex.
      std::smatch matchResults;
      if (std::regex_match(line, matchResults, _mapEntryRegex))
      {
        if (matchResults.size() != 5)
        {
          _errorStream << "Badly formed line[" << line_counter << "]: '" << line<< "'";
          _hadError = true;
          return false;
        }

        // Note: match result 0 is always the whole matched string.

        ////////////////////////////////////////////////////////
        ///
        /// Select the map in which the opcode will be stored.
        ///
        ////////////////////////////////////////////////////////

        q_map_t* opcodeMap = 0;

        if (matchResults[1] == "opcode")
        {
          // Silently ignore the 'def_opcode' lines, that might be present if
          // a previously dumped opcode qmap file is used.
          continue;
        }
        else if (matchResults[1] == "q_arg_none")
        {
          opcodeMap = &_q_inst_arg_none_opcodes;
        }
        else if (matchResults[1] == "q_arg_st")
        {
          opcodeMap = &_q_inst_arg_st_opcodes;
        }
        else if (matchResults[1] == "q_arg_tt")
        {
          opcodeMap = &_q_inst_arg_tt_opcodes;
        }
        else
        {
          // This probably cannot happen, but just in case...
          _errorStream << "Unexpected map name in line[" << line_counter << "]: '" << line<< "'";
          _hadError = true;
          return false;
        }

        ////////////////////////////////////////////////////////
        ///
        /// Get the instruction name.
        ///
        ////////////////////////////////////////////////////////
        std::string instructionName = matchResults[3];

        // Make the instruction name uppercase.
        // https://stackoverflow.com/a/17793588
        for (auto & c: instructionName) c = toupper((unsigned char)c);

        // Check if the instruction name has already been used.
        auto itInstructionName = usedInstructionNames.find(instructionName);

        if (itInstructionName != usedInstructionNames.end())
        {
          // Bad news, this instruction name has already been used before.
          _errorStream << "Instruction name '" << instructionName << "' specified on line["
                       << line_counter << "] has already been used on line["
                       << itInstructionName->second << "].";
          _hadError = true;
          return false;
        }

        ////////////////////////////////////////////////////////
        ///
        /// Parse the opcode value.
        ///
        ////////////////////////////////////////////////////////
        int opcodeValue;

        try
        {
          opcodeValue = std::stoi(matchResults[4], NULL, 0);

          if (opcodeValue < 0)
          {
            _errorStream << "Negative opcode not allowed, line[" << line_counter << "]: '"
                         << line << "'";
            _hadError = true;
            return false;
          }
          else if (opcodeValue > _maxOpcodeVal)
          {
            _errorStream << "Opcode value too high (max=" << _maxOpcodeVal
                         << "), line[" << line_counter << "]: '"
                         << line << "'";
            _hadError = true;
            return false;
          }

          // Check if the opcode value has already been used.
          auto itOpCode = usedOpcodes.find(opcodeValue);

          if (itOpCode != usedOpcodes.end())
          {
            // Bad news, this opcode has already been used before.
            _errorStream << "Opcode value (" << opcodeValue << ") specified on line["
                         << line_counter << "] has already been used on line["
                         << itOpCode->second << "].";
            _hadError = true;
            return false;
          }

          // The opcode is good to use, so store it in the appropriate map.

          (*opcodeMap)[instructionName] = opcodeValue;

          // Also store the opcode value in usedOpcodes, for diagnostic purposes.
          usedOpcodes[opcodeValue] = line_counter;

          // Same for the instruction name.
          usedInstructionNames[instructionName] = line_counter;
        }
        catch (const std::exception& e)
        {
          _errorStream << "Invalid opcode value in line[" << line_counter << "]: '"
                       << line << "'";
          _hadError = true;
          return false;
        }
      }
      else
      {
        _errorStream << "Badly formed line[" << line_counter << "]: '" << line<< "'";
        _hadError = true;
        return false;
      }
    }
    srcFile.close();

    // Now that all instruction definitions have been read, check if
    // opcode '0' is present.

    // This instruction is used as filler when only one double format
    // instruction has been specified on an assembly instruction.
    bool foundOpcodeZero = false;
    for (auto it : _q_inst_arg_none_opcodes)
    {
      if (it.second == 0)
      {
        foundOpcodeZero = true;
        break;
      }
    }

    if (!foundOpcodeZero)
    {
      _errorStream << "The Quantum instruction for opcode 0 is missing." << std::endl;
      _errorStream << "It is mandatory for correct operation of QISA-AS."  << std::endl;
      _errorStream << "Specify this using 'def_q_arg_none'."  << std::endl;
      _hadError = true;
      return false;
    }
  }
  else
  {
    _errorStream << "<Could not read from file: " << _filename << ">";
    _hadError = true;
    return false;
  }

  return true;
}

std::string
QISA_QMapParser::getLastErrorMessage()
{
  return _errorStream.str();
}

bool
QISA_QMapParser::getInstructionCodeMaps(q_map_t& arg_none_map,
                                        q_map_t& arg_st_map,
                                        q_map_t& arg_tt_map)
{
  if (_filename.empty())
  {
    _errorStream << "Nothing has been parsed yet.";
    return false;
  }

  if (_hadError)
  {
    // An error message has already been left behind.
    return false;
  }

  arg_none_map = _q_inst_arg_none_opcodes;
  arg_st_map = _q_inst_arg_st_opcodes;
  arg_tt_map = _q_inst_arg_tt_opcodes;

  return true;
}

} /* end namespace QISA */
