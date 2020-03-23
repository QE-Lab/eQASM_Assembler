#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <cstring>

#include "qisa_driver.h"

std::string usage(const std::string& progName)
{
  std::stringstream ss;
  ss << "Usage: " << progName << " [OPTIONS] INPUT_FILE" << std::endl;
  ss << "Assembler/Disassembler for the Quantum Instuction Set Architecture (QISA)." << std::endl;
  ss << std::endl;
  ss << "Options:" << std::endl;
  ss << "  -q QMAP_FILE      Load quantum instructions from given QMAP_FILE." << std::endl;
  ss << "  --dumpspecs       Output the instruction specifications that have been configured into the assembler" << std::endl;
  ss << "  -d[ 1 | 2 ]       Disassemble the given INPUT_FILE" << std::endl;
  ss << "                    Extra integer option suffix specifies the disassembly output format, default = 1" << std::endl;
  ss << "  -o OUTPUT_FILE    Save binary assembled or textual disassembled instructions to the given OUTPUT_FILE" << std::endl;
  ss << "  -t                Enable scanner and parser tracing while assembling" << std::endl;
  ss << "  -V, --version     Show the program version and exit" << std::endl;
  ss << "  -v, --verbose     Show informational messages while assembling" << std::endl;
  ss << "  -h, --help        Show this help message and exit" << std::endl;
  ss << std::endl;
  ss << "Note:" << std::endl;
  ss << "  If option -q is not given, an attempt is made to load the quantum instructions from" << std::endl;
  ss << "  the file specified in the environment variable QISA_AS_QMAP_FILE." << std::endl;
  ss << "  If -q is not given and QISA_AS_QMAP_FILE is not defined, the factory default quantum instruction" << std::endl;
  ss << "  set will be used instead." << std::endl;

  return ss.str();
}

int
main(const int argc, const char **argv)
{
  bool enableTrace = false;
  bool enableVerbose = false;
  bool doDisassemble = false;
  bool doDumpSpecs = false;
  bool doLoadQmap = false;
  const char* inputFilename = 0;
  const char* outputFilename = 0;
  const char* qmapFilename = 0;

  int disassemblyFormatId = 1;

  std::string progName = argv[0];

  // EXTRACT PROGRAM NAME

  const char pathSep =
#ifdef _WIN32
  '\\';
#else
  '/';
#endif

  size_t spos = progName.find_last_of(pathSep);
  if (spos != std::string::npos)
      progName = progName.substr(spos + 1);

  // Parse the command line arguments.
  for (int i = 1; i < argc; i++ )
  {
    const char* arg = argv[i];

    if (arg[0] == '-')
    {
      // This is an option.

      if (!std::strcmp(arg, "-h") ||
          !std::strcmp(arg, "--help"))
      {
        std::cout << usage(progName);
        return EXIT_SUCCESS;
      }

      else if (!std::strcmp(arg, "-V") ||
               !std::strcmp(arg, "--version"))
      {
        std::cout << progName << " (Quantum Instuction Set Architecture Assembler) version " << QISA::QISA_Driver::getVersion() << std::endl;
        return EXIT_SUCCESS;
      }
      else if (!std::strcmp(arg, "-v") ||
               !std::strcmp(arg, "--verbose"))
      {
        enableVerbose = true;
      }

      else if (!std::strcmp(arg, "-t"))
      {
        enableTrace = true;
      }
      else if (!std::strcmp(arg, "-q"))
      {
        qmapFilename = argv[++i];
        doLoadQmap = true;
      }
      else if (!std::strcmp(arg, "-d"))
      {
        doDisassemble = true;
        // default disassembly format is 1.
        disassemblyFormatId = 1;
      }
      else if (!std::strcmp(arg, "-d1"))
      {
        doDisassemble = true;
        disassemblyFormatId = 1;
      }
      else if (!std::strcmp(arg, "-d2"))
      {
        doDisassemble = true;
        disassemblyFormatId = 2;
      }
      else if (!std::strcmp(arg, "-o"))
      {
        outputFilename = argv[++i];
      }
      else if (!std::strcmp(arg, "--dumpspecs"))
      {
        doDumpSpecs = true;
      }
      else
      {
        std::cerr << progName << ": Unrecognized option: '" << arg << "'" << std::endl
                  << "Try " << progName << " --help for more information." << std::endl;
        return EXIT_FAILURE;
      }
    }
    else
    {
      // This command line argument is not an option.
      // Assume that this is the input filename.
      // Issue an error if an input filename has already been specified.
      if (inputFilename != 0)
      {
        std::cerr << progName << ": Too many input files specified" << std::endl
                  << "Try " << progName << " --help for more information." << std::endl;
        return EXIT_FAILURE;
      }

      inputFilename = arg;
    }
  }


  if (inputFilename == 0)
  {
    // If doDumpSpecs is specified, it is not necessary to specify an input filename.
    if (!doDumpSpecs)
    {
      std::cerr << progName << ": No input file specified?" << std::endl
                << "Try " << progName << " --help for more information." << std::endl;
      return EXIT_FAILURE;
    }
  }
  else
  {
    // Check if the given input file can be opened for reading.
    // Issue an error if not.

    std::ifstream tstFileStream(inputFilename);
    if (tstFileStream.fail())
    {
      std::cerr << progName << ": Cannot open file '" << inputFilename << "'" << std::endl;
      return EXIT_FAILURE;
    }
  }

  QISA::QISA_Driver driver;

  //driver.read();
  driver.enableScannerTracing(enableTrace);
  driver.enableParserTracing(enableTrace);
  driver.setVerbose(enableVerbose);

  if (!doLoadQmap)
  {
    const char* qmapFileFromEnv = std::getenv("QISA_AS_QMAP_FILE");
    if (qmapFileFromEnv != nullptr)
    {
      if (enableVerbose)
      {
        std::cout << "QISA-AS: Using environment (QISA_AS_QMAP_FILE) specified "
                  << "QMAP file: '" << qmapFileFromEnv << "'." << std::endl;
      }

      // Check if the specified file can be opened for reading.
      std::ifstream tstFileStream(qmapFileFromEnv);
      if (tstFileStream.good())
      {
        // If so, prepare to load this file.
        qmapFilename = qmapFileFromEnv;
        doLoadQmap = true;
      }
      else
      {
        std::cerr << progName << ": Error reading environment (QISA_AS_QMAP_FILE)"
                  << "specified QMAP file '" << qmapFileFromEnv << "'" << std::endl;
        return EXIT_FAILURE;
      }
    }
  }

  if (doLoadQmap)
  {

    bool success = driver.loadQuantumInstructions(qmapFilename);

    if (!success)
    {
      std::cerr << driver.getLastErrorMessage() << std::endl;
      return EXIT_FAILURE;
    }
  }


  if (doDumpSpecs)
  {
    std::cout << driver.dumpInstructionsSpecification() << std::endl;
    return EXIT_SUCCESS;
  }

  /* Parse the file. */
  bool success;

  if (doDisassemble)
  {
    success = driver.setDisassemblyFormat(disassemblyFormatId);
    if (success)
    {
      success = driver.disassemble(inputFilename);
    }
  }
  else
  {
    success = driver.assemble(inputFilename);
  }

  if (success)
  {
    if (outputFilename == 0)
    {
      if (doDisassemble)
      {
        std::cout << "Disassembly output:" << std::endl;
        std::cout << driver.getDisassemblyOutput();
      }
      else
      {
        std::cout << "Generated assembly (hex):" << std::endl;

        std::vector<std::string> hexStrings = driver.getInstructionsAsHexStrings(true);
        for (auto it = hexStrings.begin(); it != hexStrings.end(); ++it)
        {
          std::cout << *it << std::endl;
        }
      }
    }
    else
    {

      bool save_result = driver.save(outputFilename);

      if (!save_result)
      {
        std::cerr << "Saving terminated with errors:" << std::endl;
        std::cerr << driver.getLastErrorMessage();
        return EXIT_FAILURE;
      }
    }

    return EXIT_SUCCESS;
  }
  else
  {
    std::cerr << driver.getLastErrorMessage() << std::endl;

    if (doDisassemble)
    {
      std::cerr<< "Disassembly terminated with errors." << std::endl;
    }
    else
    {
      std::cerr << "Assembly terminated with errors." << std::endl;
    }

    return EXIT_FAILURE;
  }

}
