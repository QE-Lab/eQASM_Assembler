import os
import logging
import json
import sys

# Python script that is used to see if (when an erroneous assembly source
# file is provided) the error messages are consistent after each call to
# the QISA_Driver().
# This script can be started using python3 and by specifying the PYTHONPATH
# environment.
# A lot of output is generated, so redirect the output to a file and check
# the output of the iterations to see if there are any changes between them.

from pyQisaAs import QISA_Driver

driver = QISA_Driver()
driver.enableScannerTracing(False)
driver.enableParserTracing(False)
driver.setVerbose(True)

inputFilename = r"tst_issue_38.qisa"
outputFilename = r"tst_issue_38.bin"
disassemblyOutputFilename = r"tst_issue_38_disass.txt"
qmapFilename = r"tst_issue_38.qmap"

qisa_as_version = QISA_Driver.getVersion()
print ("QISA_AS Version: ", qisa_as_version)

version_parts = [int(x) for x in qisa_as_version.split('.')]
qisa_as_major_version = version_parts[0]

# For QISA-AS v2, we load the quantum instructions from a file.
if qisa_as_major_version >= 2:
    print ("Loading quantum instruction set from file ", qmapFilename)
    success = driver.loadQuantumInstructions(qmapFilename)
    if not success:
        print ("Failed to load quantum instructions from file '{}'.".format(qmapFilename))
        print ("Error: ", driver.getLastErrorMessage())
        exit(1)

for iteration in range(100):
    print ("ITERATION: {} ===========================================".format(iteration))
    sys.stdout.flush()
    if qisa_as_major_version >= 2:
        print ("assembling file ", inputFilename)
        success = driver.assemble(inputFilename)
    else:
        print ("parsing file ", inputFilename)
        success = driver.parse(inputFilename)

    if success:
        print ("Generated instructions:")
        instHex = driver.getInstructionsAsHexStrings(False)
        for inst in instHex:
            print ("  " + inst)
        print()

        print ("Generated instructions, including binary:")
        instHexBin = driver.getInstructionsAsHexStrings(True)
        for inst in instHexBin:
            print ("  " + inst)
        print()

        print ("Saving instructions to file: ", outputFilename)
        success = driver.save(outputFilename)
        if success:
            print ("Disassembling saved instructions from file: ", outputFilename)

            success = driver.disassemble(outputFilename)
            if success:
                print(driver.getDisassemblyOutput())

                print ("Saving disassembly to file: ", disassemblyOutputFilename)
                success = driver.save(disassemblyOutputFilename)
                if not success:
                    print ("Saving disassembly terminated with errors:")
                    print (driver.getLastErrorMessage())
                    sys.stdout.flush()
            else:
                print ("Disassembly terminated with errors:")
                print (driver.getLastErrorMessage())
                sys.stdout.flush()
        else:
            print ("Saving assembly terminated with errors:")
            print (driver.getLastErrorMessage())
            sys.stdout.flush()
    else:
        print ("Assembly terminated with errors:")
        print (driver.getLastErrorMessage())
        sys.stdout.flush()
