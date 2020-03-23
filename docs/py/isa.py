from operation import *
import os
import sys
sys.path.insert(0, os.getcwd())


rd_format = [24, 20, "Rd"]
rs_format = [19, 15, "Rs"]
rt_format = [14, 10, "Rt"]
opcode_range = [30, 25]
MSb_dict = {
    "position": 31,
    "single_format": "0",
    "bundle": "1"
}

isa_dict = {
    "single_format": {
        "nop": {
            "full_name": "No Operation",
            "opcode": "000000",
            "offset": [24, 4, "0"*21],
            "cond": [3, 0, "0000"]
        },
        # "goto": {
        #     "full_name": "Goto",
        #     "opcode": "000001",
        #     "offset": [24, 4, "imm"],
        #     "cond": [3, 0, "0000"]
        # },

        "br": {
            "full_name": "Branch",
            "opcode": "000001",
            "offset": [24, 4, "imm"],
            "cond": [3, 0, "comp\_flag"]
        },

        "stop": {
            "full_name": "Stop",
            "opcode": "001000",
            "reserved": [24, 0, "reserved"]
        },

        # "test": {
        #     "opcode": "001100",
        #     "reserved0": [24, 20, "reserved"],
        #     "rs": True,
        #     "rt": True,
        #     "reserved1": [9, 0, "reserved"]
        # },

        "cmp": {
            "full_name": "Compare",
            "opcode": "001101",
            "reserved0": [24, 20, "reserved"],
            "rs": True,
            "rt": True,
            "reserved1": [9, 0, "reserved"]
        },

        "fbr": {
            "full_name": "Fetch Branch Register (Comparison Flag)",
            "opcode": "010100",
            "rd": True,
            "reserved": [19, 4, "reserved"],
            "cond": [3, 0, "comp\_flag"]
        },

        "fmr": {
            "full_name": "Fetch Measurement Result",
            "opcode": "010101",
            "rd": True,
            "reserved": [19, 3, "reserved"],
            "cond": [2, 0, "Qi"]
        },

        "ldi": {
            "full_name": "Load Immediate",
            "opcode": "010110",
            "rd": True,
            "imm": [19, 0, "imm"]
        },

        "ldui": {
            "full_name": "Load Unsigned Immediate",
            "opcode": "010111",
            "rd": True,
            "rs": True,
            "imm": [14, 0, "imm"]
        },

        "ld": {
            "full_name": "Load Word from Memory",
            "opcode": "001001",
            "rd": True,
            "reserved": [19, 15, "reserved"],
            "rt": True,
            "imm": [9, 0, "imm"]
        },

        "st": {
            "full_name": "Store Word to Memory",
            "opcode": "001010",
            "reserved": [24, 20, "reserved"],
            "rs": True,
            "rt": True,
            "imm": [9, 0, "imm"]
        },

        "or": {
            "full_name": "Or",
            "opcode": "011000",
            "rd": True,
            "rs": True,
            "rt": True,
            "reserved": [9, 0, "imm"]
        },

        "xor": {
            "full_name": "Exclusive Or",
            "opcode": "011001",
            "rd": True,
            "rs": True,
            "rt": True,
            "reserved": [9, 0, "imm"]
        },

        "and": {
            "full_name": "And",
            "opcode": "011010",
            "rd": True,
            "rs": True,
            "rt": True,
            "reserved": [9, 0, "imm"]
        },

        "not": {
            "full_name": "Not",
            "opcode": "011011",
            "rd": True,
            "rt": True,
            "reserved0": [9, 0, "reserved"],
            "reserved1": [19, 15, "reserved"]
        },

        # "addc": {
        #     "full_name": "Addition with Carry",
        #     "opcode": "011100",
        #     "rd": True,
        #     "rs": True,
        #     "rt": True,
        #     "reserved": [9, 0, "reserved"],
        # },

        # "subc": {
        #     "full_name": "Subtraction with Carry",
        #     "opcode": "011101",
        #     "rd": True,
        #     "rs": True,
        #     "rt": True,
        #     "reserved": [9, 0, "reserved"],
        # },

        "add": {
            "full_name": "Add",
            "opcode": "011110",
            "rd": True,
            "rs": True,
            "rt": True,
            "reserved": [9, 0, "reserved"],
        },

        "sub": {
            "full_name": "Subtraction",
            "opcode": "011111",
            "rd": True,
            "rs": True,
            "rt": True,
            "reserved": [9, 0, "reserved"],
        },

        "qwait": {
            "full_name": "Quantum Wait Immediate",
            "opcode": "100000",
            "reserved": [24, 20, "reserved"],
            "imm": [19, 0, "Imm20"],
        },

        "qwaitr": {
            "full_name": "Quantum Wait Register",
            "opcode": "100001",
            "reserved0": [24, 20, "reserved"],
            "rs": True,
            "reserved1": [14, 0, "reserved"],
        },

        # "smis": {
        #     "full_name": "Set Mask Immediate for Singe-qubit Operations",
        #     "opcode": "100000",
        #     "sd": [24, 19, "Sd"],
        #     "reserved": [18, 7, "reserved"],
        #     "mask": [6, 0, "Imm7"],
        # },

        # "smit": {
        #     "full_name": "Set Mask Immediate for Two-qubit Operations",
        #     "opcode": "101000",
        #     "sd": [24, 19, "Td"],
        #     "reserved": [18, 16, "reserved"],
        #     "mask": [15, 0, "Imm16"],
        # },
    }
}


def is_binary(num):
    try:
        int(num, 2)
        return True
    except ValueError:
        return False


def resolve_dict(isa_dict):
    new_dict = {}
    for format_key, format_insn_dict in isa_dict.items():
        for insn_name, insn_content in format_insn_dict.items():

            insn_info = {
                "full_name": None,
                "fields": None
            }

            insn_fields = {}
            if format_key == "single_format":
                insn_fields["MSb"] = [MSb_dict["position"],
                                      MSb_dict["single_format"]]
            else:
                insn_fields["MSb"] = [MSb_dict["position"],
                                      MSb_dict["bundle"]]

            for field_name, field_prop_value in insn_content.items():
                if field_name.lower() == "full_name":
                    insn_info["full_name"] = field_prop_value
                elif field_name == "opcode":
                    if not is_binary(field_prop_value):
                        raise ValueError(
                            "Given opcode is not binary({}).".format(
                                field_prop_value))

                    if len(field_prop_value) != 6:
                        raise ValueError("Given opcode length ({}) does"
                                         " not match required ({}).".format(
                                             len(field_prop_value), 6))

                    insn_fields["opcode"] = [opcode_range[0],
                                             opcode_range[1],
                                             field_prop_value]

                elif field_name.lower() == "rd":
                    insn_fields["rd"] = rd_format
                elif field_name.lower() == "rs":
                    insn_fields["rs"] = rs_format
                elif field_name.lower() == "rt":
                    insn_fields["rt"] = rt_format
                else:
                    if (not isinstance(field_prop_value, list)) or \
                       (len(field_prop_value) != 3):
                        raise ValueError("Given field format not correct: ",
                                         field_prop_value)
                    if field_name.lower().startswith("reserve"):
                        field_prop_value[2] = r"\reserved"
                    if field_prop_value[2] == "imm":
                        field_prop_value[2] = "imm{}".format(
                            field_prop_value[0] - field_prop_value[1] + 1)
                    insn_fields[
                        field_name.lower()] = field_prop_value

            if insn_info["full_name"] is None:
                raise ValueError("The full name is not given of the "
                                 "instruction {}".format(insn_name.lower()))

            # sort the insn_field_property dictionary according to the field
            #   range and save it as a list
            print(insn_fields)
            keys = sorted(insn_fields,
                          key=lambda x: insn_fields[x][0],
                          reverse=True)
            sorted_insn_fields = [
                [key, insn_fields[key]] for key in keys]

            check_completeness(insn_name.lower(), sorted_insn_fields)

            insn_info["fields"] = sorted_insn_fields

            new_dict[insn_name.lower()] = insn_info

    print("new_dict:")
    for key, value in new_dict.items():
        print(key, ": ", value)
    return new_dict


def check_completeness(insn_name, insn_fields):
    if not isinstance(insn_fields, list):
        raise ValueError("{}: Given insn_fields ({}) is not a list."
                         " \nFields are: {}".format(insn_name,
                                                    type(insn_fields), insn_fields))
    expected_pos = 31
    for field in insn_fields:
        if field[1][0] != expected_pos:
            raise ValueError("{}: Given fields position ({}) does not match "
                             "expected({}).\nFields are: {}".format(insn_name,
                                                                    field[1][0], expected_pos, insn_fields))

        if len(field[1]) == 2:
            expected_pos = expected_pos - 1
        else:
            if field[1][1] > expected_pos:
                raise ValueError("{}: Given fields position is incorrect:"
                                 "({}, {}).\nFields are: {}".format(insn_name,
                                                                    field[1][0], field[1][1], insn_fields))
            expected_pos = field[1][1] - 1


def gen_row_content(name, field_list):

    fields = field_list

    row_string = ""
    font = "\\small"
    for field in fields:
        field_str = ""
        field_name = field[0]
        field_info = field[1]
        if len(field_info) == 2:
            field_length = 1
            field_pos_len = 1
        else:
            field_pos_len = 2
            field_length = field_info[0] - field_info[1] + 1

        field_value = field_info[field_pos_len]
        is_binary_str = is_binary(field_value)

        if is_binary_str:
            if len(field_value) != field_length:
                raise ValueError("field length ({}) does not match. "
                                 "field: {}".format(field_length, field))

            for i in range(len(field_value)):
                # left vertical bar: only added when it is the first bit
                # right vertical bar: only added when the last bit is 0
                # "&" symbol: added for each bit, except the last bit is 0.
                # comment: added only for the first bit
                left_vertical_bar = " "
                right_vertical_bar = " "
                new_col_symbol = "& "
                comment = ""

                if i == 0:       # judge left vertical bar
                    left_vertical_bar = "|"
                    comment = "% {:>8s}: pos: {:>10s}, value: {}".format(
                        field_name,
                        str(field_info[0:field_pos_len]),
                        field_value)

                # judge right vertical bar
                if (i == len(field_value) - 1) and \
                        (len(field_value) - field_info[0] == 1):
                    right_vertical_bar = "|"

                # judge the new column symbol
                if (i == len(field_value) - 1) and \
                        (len(field_value) - field_info[0] == 1):
                    new_col_symbol = " "

                field_str += "\multicolumn{ 1}{" + left_vertical_bar +\
                             "@{}c@{}" + right_vertical_bar + "}{" +\
                             font + " {:>10}".format(field_value[i]) + "} " +\
                    new_col_symbol + comment + "\n"

        else:
            right_vertical_bar = " "
            new_col_symbol = "& "

            # if this field reaches the end of the instruction
            if ((field_pos_len == 1 and field_info[0] == 0) or
                    (field_pos_len == 2 and field_info[1] == 0)):
                right_vertical_bar = "|"
                new_col_symbol = "  "

            comment = "% {:>8s}: pos: {:>10s}, value: {}".format(
                field_name,
                str(field_info[0:field_pos_len]),
                field_value)

            field_str += "\multicolumn{" + "{:2}".format(field_length) +\
                         "}{|@{}c@{}" + right_vertical_bar + "}{" + font +\
                         " {:>10}".format(field_value) + "} " +\
                         new_col_symbol + comment + "\n"

        row_string += field_str
    row_string += "\\\\ \n\cline{1-32}"

    return row_string


def gen_table_4_insn(name, field_list):
    caption = "\caption{{{0} instruction encoding.}}".format(name.upper())
    table_label = "\\label{{tab:insn-{0}}}".format(name.lower())
    row_content = gen_row_content(name, field_list)

    table = ["\\begin{table}[H]",
             "\centering",
             "\\begin{isatable}",
             row_content,
             "\\end{isatable}",
             # caption,
             # table_label,
             "\\end{table}"]

    return table


def get_insn_desc(name):
    try:
        return (r"\textbf{Description:}" + "\n" +
                r"\begin{adjustwidth}{1cm}{1cm}" + "\n" +
                "{}\n".format(op_dict[name][0])
                + r"\end{adjustwidth}" + "\n")
    except:
        print("Error for the instruction:", name)
        raise


def get_insn_assembly_format(name):
    try:
        syntax_str = r"\quad\textbf{Format}: \hspace{4cm} \lstinline[basicstyle=\normalsize\ttfamily]!" + \
            op_dict[name][1] + "!\n"
    except:
        print("Error for the instruction:", name)
        raise

    return syntax_str


def get_insn_op(name):
    try:
        op_content = op_dict[name][2]
    except:
        print("Error for the instruction:", name)
        raise
    op_behavior_env = "OpBehavior"
    op_str = "\\textbf{Operation}:\n"
    op_str += "\\begin{" + op_behavior_env + "}\n" + op_content + "\n\\end{" +\
              op_behavior_env + "}\n"
    return op_str


def gen_insn_full_section(outfile, name, insn_info):
    section_header = "\subsection{{ {0} -- {1} }}\label{{sec:insn-{2}}}".format(
        name.upper(), insn_info["full_name"], name.lower())

    insn_assembly_format = get_insn_assembly_format(name)
    insn_desc = get_insn_desc(name)
    insn_op = get_insn_op(name)

    insn_section_all_content = [section_header]
    insn_section_all_content.extend(
        gen_table_4_insn(name, insn_info["fields"]))
    insn_section_all_content.append(r"\vspace{-0.4cm}" + "\n")
    insn_section_all_content.append(insn_assembly_format)
    insn_section_all_content.append(insn_desc)
    insn_section_all_content.append(insn_op)

    for line in insn_section_all_content:
        outfile.write(line)
        outfile.write("\n")

    outfile.write('\n\n')


def gen_tex(all_insn_info, filename):
    with open(filename, 'w') as outfile:
        for insn_name, insn_info in sorted(all_insn_info.items()):
            if insn_name == "stop":
                outfile.write("\\input{isa/smi.tex}\n\n")
            gen_insn_full_section(outfile, insn_name, insn_info)


all_insn_info = resolve_dict(isa_dict)
gen_tex(all_insn_info, r"D:\GitHub\eQASM_Assembler\docs\tmp.tex")
# gen_tex("D:\Dropbox (Personal)\Share\ShareLaTeX\CCLight_eQASM\insn_encoding.tex")
