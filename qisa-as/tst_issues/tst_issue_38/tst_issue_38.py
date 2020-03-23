import os
import logging
import json
import sys

# Python script that has been uploaded with GitHub issue 38.
# It has been modified so that it can cope with both the old 'v1' and the new
# 'v2' assembler.
# Also, the hardcoded path to the assembler build directory has been removed.
# It can be specified using the PYTHONPATH environment.
# This way, the source doesn't have to be changed for each build environment

from qisa_as import QISA_Driver

driver = QISA_Driver()
driver.enableScannerTracing(False)
driver.enableParserTracing(False)
driver.setVerbose(True)

rootDir = os.path.dirname(os.path.realpath(__file__))

inputFilename = os.path.join(rootDir, 'tst_issue_38.qisa')
outputFilename = os.path.join(rootDir, 'tst_issue_38.bin')
disassemblyOutputFilename = os.path.join(rootDir, 'tst_issue_38_disass.txt')
qmapFilename = os.path.join(rootDir, 'tst_issue_38.qmap')

qisa_as_version = QISA_Driver.getVersion()
print ("QISA_AS Version: ", qisa_as_version)

version_parts = [int(x) for x in qisa_as_version.split('.')]
qisa_as_major_version = version_parts[0];


if qisa_as_major_version >= 2:
# For QISA-AS v2, we load the quantum instructions from a file.
    print ("Loading quantum instruction set from file ", qmapFilename)
    success = driver.loadQuantumInstructions(qmapFilename)
    if success:
        print ("assembling file ", inputFilename)
        success = driver.assemble(inputFilename)
    else:
        print ("Failed to load quantum instructions from file '{}'.".format(qmapFilename))
        print ("Error: ", driver.getLastErrorMessage())
        exit(1)
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
        else:
            print ("Disassembly terminated with errors:")
            print (driver.getLastErrorMessage())
    else:
        print ("Saving assembly terminated with errors:")
        print (driver.getLastErrorMessage())
else:
    print ("Assembly terminated with errors:")
    print (driver.getLastErrorMessage())
