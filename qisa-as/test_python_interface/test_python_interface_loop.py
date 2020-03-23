# This test is used to assert that the results do not change when multiple
# assemble/disassemble cycles are executed without creating a new
# QISA_Driver() instance.

import sys

# Note: We must import qisa_qmap, which is used to pass dictionaries to the
# driver.
from qisa_as import QISA_Driver, qisa_qmap
import os

# Note: the file ../qisa_test_assembly/test_assembly.qisa can be assembled
# using the factory default quantum instructions.
rootDir = os.path.dirname(os.path.realpath(__file__))

inputFilename = os.path.join(rootDir, 'qisa_test_assembly/test_assembly.qisa')
outputFilename = 'test_assembly.out'
disassemblyOutputFilename = 'test_disassembly.out'

outputFilename_loop = 'test_assembly_loop.out'

print ("QISA_AS Version: ", QISA_Driver.getVersion())

driver = QISA_Driver()

# print the instructions specification.
# This should reflect the classic instruction set and the factory default
# quantum instruction set.
print ("Retrieving QISA Instructions specification...")
print (driver.dumpInstructionsSpecification())

driver.enableScannerTracing(False)
driver.enableParserTracing(False)
driver.setVerbose(False)

print ("Init: Assembling file ", inputFilename)
success = driver.assemble(inputFilename)

if not success:
    print ("Assembly terminated with errors:")
    print (driver.getLastErrorMessage())
    exit(1)

instHex_orig = driver.getInstructionsAsHexStrings(False)

print ("Init: Saving instructions to file: ", outputFilename)
success = driver.save(outputFilename)
if not success:
    print ("Saving assembly terminated with errors:")
    print (driver.getLastErrorMessage())
    exit(1)

print ("Init: Disassembling saved instructions from file: ", outputFilename)

success = driver.disassemble(outputFilename)
if not success:
    print ("Disassembly terminated with errors:")
    print (driver.getLastErrorMessage())
    exit(1)

disassembly_orig = driver.getDisassemblyOutput()

# Now we have the necessary reference variables to check against.
# Start the same functions again, in a loop, and check the generated
# results against the reference variables.

for iteration in range(100):
    print ("ITERATION: {} ===========================================".format(iteration))
    sys.stdout.flush()

    success = driver.assemble(inputFilename)

    if not success:
        print ("Assembly terminated with errors:")
        print (driver.getLastErrorMessage())
        exit(1)

    instHex_loop = driver.getInstructionsAsHexStrings(False)

    if instHex_loop != instHex_orig:
        print ("Differences detected in getInstructionsAsHexStrings() output.")
        exit(1)

    success = driver.save(outputFilename_loop)
    if not success:
        print ("Saving assembly terminated with errors:")
        print (driver.getLastErrorMessage())
        exit(1)

    success = driver.disassemble(outputFilename_loop)
    if not success:
        print ("Disassembly terminated with errors:")
        print (driver.getLastErrorMessage())
        exit(1)

    disassembly_loop = driver.getDisassemblyOutput()

    if disassembly_loop != disassembly_orig:
        print ("Differences detected in getDisassemblyOutput() output.")
        exit(1)

    # If we arrive here, all is good.
    print ("\t TESTS PASS")
    sys.stdout.flush()

print ()
print ("====================")
print ("=                  =")
print ("= ALL TESTS PASSED =")
print ("=                  =")
print ("====================")
