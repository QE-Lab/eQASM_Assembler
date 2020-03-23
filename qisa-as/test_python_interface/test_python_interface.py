# Note: We must import qisa_qmap, which is used to pass dictionaries to the
# driver.
from qisa_as import QISA_Driver, qisa_qmap
import os

# Note: the file ../qisa_test_assembly/test_assembly.qisa can be assembled
# using the factory default quantum instructions.

rootDir = os.path.dirname(os.path.realpath(__file__))

inputFilename = os.path.join(rootDir, 'qisa_test_assembly/test_assembly.qisa')
outputFilename = 'test_assembly.out'
disassemblyFormat1OutputFilename = 'test_disassembly_format_1.out'
disassemblyFormat2OutputFilename = 'test_disassembly_format_2.out'

print ("QISA_AS Version: ", QISA_Driver.getVersion())

driver = QISA_Driver()

# print the instructions specification.
# This should reflect the classic instruction set and the factory default
# quantum instruction set.
print ("Retrieving QISA Instructions specification...")
print (driver.dumpInstructionsSpecification())

driver.enableScannerTracing(False)
driver.enableParserTracing(False)
driver.setVerbose(True)

print ("parsing file ", inputFilename)
success = driver.assemble(inputFilename)

if not success:
  print ("Assembly terminated with errors:")
  print (driver.getLastErrorMessage())
  exit()

print ("Generated instructions:")
instHex = driver.getInstructionsAsHexStrings(False)
for inst in instHex:
  print ("  " + inst)
print()

print ("Generated instructions, including binary representation:")
instHexBin = driver.getInstructionsAsHexStrings(True)
for inst in instHexBin:
  print ("  " + inst)
print()

print ("Saving instructions to file: ", outputFilename)
success = driver.save(outputFilename)

if not success:
  print ("Saving assembly terminated with errors:")
  print (driver.getLastErrorMessage())
  exit()

print ("Disassembling saved instructions from file: ", outputFilename)
print ("Use default disassembly output format (1).")

success = driver.disassemble(outputFilename)
if not success:
  print ("Disassembly terminated with errors:")
  print (driver.getLastErrorMessage())
  exit()

print(driver.getDisassemblyOutput())

print ("Saving disassembly to file: ", disassemblyFormat1OutputFilename)
success = driver.save(disassemblyFormat1OutputFilename)

if not success:
  print ("Saving disassembly terminated with errors:")
  print (driver.getLastErrorMessage())
  exit()

print ("Use disassembly output format 2.")

driver.setDisassemblyFormat(2)

print(driver.getDisassemblyOutput())

print ("Saving disassembly to file: ", disassemblyFormat2OutputFilename)
success = driver.save(disassemblyFormat2OutputFilename)

if not success:
  print ("Saving disassembly terminated with errors:")
  print (driver.getLastErrorMessage())
  exit()

# Now try to parse another assembly with a quantum instruction set that is
# provided by Python dictionaries.

# Note: For disassembly, we always need to specify a quantum instruction
# without arguments and opcode 0.
# This is because opcode 0 is used as filler instruction when a double
# instruction format is specified with only one instruction.
arg_none_dict = {'QINSTR_NOP'    : 0,  'QINSTR_NO_ARGS' : 1}
arg_st_dict   = {'QINSTR_ST_001' : 10, 'QINSTR_ST_002'  : 11, 'QINSTR_ST_003' : 12}
arg_tt_dict   = {'QINSTR_TT_001' : 20, 'QINSTR_TT_002'  : 21, 'QINSTR_TT_003' : 22}

print ("Try loading quantum instructions from DICTIONARIES...")
success = driver.loadQuantumInstructions(qisa_qmap(arg_none_dict),
                                        qisa_qmap(arg_st_dict),
                                        qisa_qmap(arg_tt_dict))

if success:
    print ("Done.")
    print ("Retrieving QISA Instructions specification...")
    print (driver.dumpInstructionsSpecification())

    inputFilename = './test_python_dict.qisa'
    print ("Now parsing file ", inputFilename)
    success = driver.assemble(inputFilename)
    if success:
        print ("Generated instructions:")
        instHex = driver.getInstructionsAsHexStrings(False)
        for inst in instHex:
            print ("  " + inst)
        print()
    else:
        print ("Assembly terminated with errors:")
        print (driver.getLastErrorMessage())
        exit()

else:
    print ("Failed to load quantum instructions from dictionaries.")
    print ("Error: ", driver.getLastErrorMessage())

# Now, for completeness, do the same but load the instructions from file.
# The same output should be generated.
print ("Try loading quantum instructions from FILE...")

qmapFilename = './test_load_qmap_file.qmap'

success = driver.loadQuantumInstructions(qmapFilename)

if success:
    print ("Done.")
    print ("Retrieving QISA Instructions specification...")
    print (driver.dumpInstructionsSpecification())

    inputFilename = './test_python_dict.qisa'
    print ("Now parsing file ", inputFilename)
    success = driver.assemble(inputFilename)
    if success:
        print ("Generated instructions:")
        instHex = driver.getInstructionsAsHexStrings(False)
        for inst in instHex:
            print ("  " + inst)
        print()
    else:
        print ("Assembly terminated with errors:")
        print (driver.getLastErrorMessage())
        exit()

else:
    print ("Failed to load quantum instructions from file '{}'.".format(qmapFilename))
    print ("Error: ", driver.getLastErrorMessage())
