# This program is used to generate the configurable parts of the QISA-AS,
# so that QISA-AS knows the opcodes of the classic and quantum
# instructions.
# The file given as the '-d' argument is used as a source of the
# instruction definitions.
# The source directory of QISA-AS contains an example instruction
# definitions file named 'qisa_opcodes.qmap'.
# See that file for information on how to specify the necessary fields.
# This program uses this file in order to produce a C++ file (-co option)
# that is included in the assembler at build time.

import os.path
import string

# Parse command line arguments.
import argparse
parser = argparse.ArgumentParser(
    description="Generate instruction opcodes from a qisa instructions definitions file.")
parser.add_argument('-d', '--def-file', metavar='DEF_FILE',
                    dest='def_file',
                    required=True,
                    help="QISA instructions definition file")

parser.add_argument('-co', '--cpp-output', metavar='CPP_OUTPUT_FILE',
                    dest='cpp_output',
                    required=True,
                    help="Destination cpp output file")

args = parser.parse_args()

# A classic opcode has 6 bits.
max_c_opcode = 2**6 - 1

# A quantum opcode has 8 bits.
max_q_opcode = 2**8 - 1

def_opcode={}
def_q_arg_none={}
def_q_arg_st={}
def_q_arg_tt={}


used_c_opcodes = []
used_q_opcodes = []

exec(open(args.def_file).read())

# For the purpose of handling the quantum instruction definitions, we merge
# all quantum instruction definitions into one dictionary.
q_all = def_q_arg_none.copy()
q_all.update(def_q_arg_st)
q_all.update(def_q_arg_tt)

# ---------------------
# Handle the cpp output
# ---------------------

encountered_error = False

try:
    with open(args.cpp_output, 'w') as fd:
        print('/*' + ('*' * 76) + '*/', file=fd)
        print('/* ' + 'Automatically generated, do not edit.'.ljust(75) + '*/', file=fd)
        print('/*' + ('*' * 76) + '*/\n\n', file=fd)
        print('namespace QISA {\n', file=fd)
        print('void', file=fd)
        print('QISA_Driver::setOpcodes()', file=fd)
        print('{', file=fd)

        print('', file=fd)
        print('  // Opcodes for the Classic Instructions (Single Instruction Format)', file=fd)
        for inst,opc in sorted(def_opcode.items(), key=lambda x: x[1]):
            if ((opc < 0) or
                (opc > max_c_opcode)):
                print("Opcode for '{0}' ({1}) is out of range. Acceptable range = [0,{2}]".format(inst, opc, max_c_opcode))
                encountered_error = True
                break
            if opc in used_c_opcodes:
                print("Opcode for '{0}' ({1}) has already been used.".format(inst, opc))
                encountered_error = True
                break
            used_c_opcodes.append(opc)

            print('  _opcodes["{0}"]'.format(inst.upper()).ljust(40) +
                  "= {0:#04x};".format(opc), file=fd)

        print('', file=fd)
        print('  // Reverse lookup of above', file=fd)

        for inst,opc in sorted(def_opcode.items(), key=lambda x: x[1]):
            print('  _classicOpcode2instName[{0:#04x}]'.format(opc).ljust(40) +
                  '= "{0}";'.format(inst.upper()), file=fd)

        print('', file=fd)
        print('  ///////////////////////////////////////////////////////////////////////////////////', file=fd)
        print('  /// ', file=fd)
        print('  /// Default specification of the Quantum Instructions (Double Instruction Format)', file=fd)
        print('  /// They can be overriden by the setQuantumInstructions() function.', file=fd)
        print('  /// ', file=fd)
        print('  ///////////////////////////////////////////////////////////////////////////////////', file=fd)

        # First do some error checking on the provided values.
        if not encountered_error:
            for inst,opc in sorted(q_all.items(), key=lambda x: x[1]):
                if ((opc < 0) or
                    (opc > max_q_opcode)):
                    print("Opcode for '{0}' ({1}) is out of range. Acceptable range = [0,{2}]".format(inst, opc, max_q_opcode))
                    encountered_error = True
                    break
                if opc in used_q_opcodes:
                    print("Opcode for '{0}' ({1}) has already been used.".format(inst, opc))
                    encountered_error = True
                    break
                used_q_opcodes.append(opc)

            # Opcode 0 is used as 'filler' for the double instruction
            # format, when only one instruction has been specified in
            # assembly.
            if 0 not in def_q_arg_none.values():
                print("Opcode 0 is mandatory so an instruction for it must be defined (using def_q_arg_none).")
                encountered_error = True

        if not encountered_error:

            print('', file=fd)
            print('  // Defines the quantum instructions that do not expect an argument.', file=fd)

            for inst,opc in sorted(def_q_arg_none.items(), key=lambda x: x[1]):
                print('  _q_inst_arg_none_opcodes["{0}"]'.format(inst.upper()).ljust(40) +
                      "= {0:#04x};".format(opc), file=fd)

            print('', file=fd)
            print('  // Defines the quantum instructions that expect an S-register argument.', file=fd)

            for inst,opc in sorted(def_q_arg_st.items(), key=lambda x: x[1]):
                print('  _q_inst_arg_st_opcodes["{0}"]'.format(inst.upper()).ljust(40) +
                      "= {0:#04x};".format(opc), file=fd)

            print('', file=fd)
            print('  // Defines the quantum instructions that expect a T-register argument.', file=fd)

            for inst,opc in sorted(def_q_arg_tt.items(), key=lambda x: x[1]):
                print('  _q_inst_arg_tt_opcodes["{0}"]'.format(inst.upper()).ljust(40) +
                      "= {0:#04x};".format(opc), file=fd)

            print('', file=fd)
            print('  // Reverse lookup of all quantum instructions.', file=fd)

            for inst,opc in sorted(q_all.items(), key=lambda x: x[1]):
                print('  _quantumOpcode2instName[{0:#04x}]'.format(opc).ljust(40) +
                      '= "{0}";'.format(inst.upper()), file=fd)

        if not encountered_error:
            print('}\n', file=fd)
            print('} // namespace QISA', file=fd)

except Exception as e:
    print("Exception occured while writing to file '{0}': {1}".format(args.cpp_output, e))
    error_encountered = True

# Remove the generated file upon error
if encountered_error:
    try:
        os.remove(args.cpp_output)
    except:
        pass
    sys.exit(1)  # Exit with code 1 to indicate failure.
