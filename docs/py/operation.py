# The structure of the operation dictionary is:
#  - Description
#  - Assembly format
#  - Pesudo code describing its operation
op_dict = {
"nop":[
r"The \lstinline!NOP! instruction performs no operation.",
"NOP",
'''PC = PC + 4
'''],

"add":[
r"The \lstinline!ADD! instruction adds two GPR (\code{Rs}, \code{Rt}) values, and writes the result to the destination GPR (\code{Rd}) .",
"ADD Rd, Rs, Rt",
'''integer sum = UInt(GPR_val(Rs), 32) + UInt(GPR_val(Rt), 32)
GPR(Rd) = ToUBitStr(sum, 32)
PC = PC + 4
# NOTE, with 2's complement binary, it is the same for signed addition.
'''],

"sub":[
r"The \lstinline!SUB! instruction subtract a GPR (\code{Rs}) value from another GPR (\code{Rt}) value, and writes the result to the destination GPR (\code{Rd}).",
"SUB Rd, Rs, Rt",
'''integer sum = UInt(GPR_val(Rs), 32) + UInt(NOT(GPR_val(Rt)), 32) + UInt(1, 32)
GPR(Rd) = ToUBitStr(sum, 32)
PC = PC + 4
# NOTE, with 2's complement binary, it is the same for signed subtraction.
'''],

"addc":[
r"The \lstinline!ADDC! instruction adds two GPR (\code{Rs}, \code{Rt}) values, and writes the result to the destination GPR (\code{Rd}). In addition, it sets the execution flags.",
"ADDC Rd, Rs, Rt",
'''integer sum = UInt(Rs, 32) + UInt(Rt, 32)
GPR(Rd) = ToUBitStr(sum, 32)
setExeFlagB()
PC = PC + 4
'''],

"subc":[
r"The \lstinline!SUBC! instruction subtract a GPR  (\code{Rs}) value from another GPR (\code{Rt}) value, and writes the result to the destination GPR (\code{Rd}). In addition, it sets the execution flags.",
"SUBC Rd, Rs, Rt",
'''integer sum = UInt(Rs, 32) + UInt(NOT(Rt), 32) + UInt(1, 32)
GPR(Rd) = ToUBitStr(sum, 32)
setExeFlagA()
PC = PC + 4
'''],

"goto":[
r"The \lstinline!GOTO! instruction changes the flow of execution unconditionally by adding an immediate offset to \lstinline!PC! that fetched the instruction. It is an alias of the instruction \lstinline!BR always, <label>!.",
"GOTO <label>",
'''integer sum = SInt(PC, 17) + SInt(Imm21[14:0] << 2, 17)
PC = ToSBitStr(signed_sum, 18)[16:0]
'''],

"br":[
r"If the specified comparison flag is `1', the \lstinline!BR! instruction changes the PC by adding an immediate offset to it. Table~\ref{tab:cmp_flags} lists all allowed comparison flags and the corresponding meaning in eQASM. <label> points to the target instruction. The assembler is responsible for converting the <label> to the immediate value \code{Imm21} according to the relative position of the target instruction and this \lstinline!BR! instruction.",
"BR <comp_flag>, <label>",
'''if CompFlag_val(comp_flag) == '1':
    integer signed_sum = SInt(PC, 17) + SInt(Imm21[14:0] << 2, 17)
    PC = ToSBitStr(signed_sum, 18)[16:0]
end if
'''],

"stop":[
r"The \lstinline!STOP! instruction sets the execution flag \code{STOP}, and repeats executing itself infinitely. In other words, it stops the processor.",
"STOP",
'''EXEFLAG.STOP = 1
PC = PC
'''],

"cmp":[
r"The \lstinline!CMP! instruction compares the value of two GPRs (\code{Rs}, \code{Rt}), and updates the comparison flags based on the results.",
"CMP Rs, Rt",
'''COMPFLAG.ALWAYS = 1
COMPFLAG.NEVER = 0
COMPFLAG.EQ  = (GPR_val(Rt) == GPR_val(Rs))
COMPFLAG.NE  = (GPR_val(Rt) != GPR_val(Rs))
COMPFLAG.LTU = (UInt(GPR_val(Rt), 32) < UInt(GPR_val(Rs), 32))
COMPFLAG.GEU = (UInt(GPR_val(Rt), 32) >= UInt(GPR_val(Rs), 32))
COMPFLAG.LEU = (UInt(GPR_val(Rt), 32) <= UInt(GPR_val(Rs), 32))
COMPFLAG.GTU = (UInt(GPR_val(Rt), 32) > UInt(GPR_val(Rs), 32))
COMPFLAG.LT  = (SInt(GPR_val(Rt), 32) < SInt(GPR_val(Rs), 32))
COMPFLAG.GE  = (SInt(GPR_val(Rt), 32) >= SInt(GPR_val(Rs), 32))
COMPFLAG.LE  = (SInt(GPR_val(Rt), 32) <= SInt(GPR_val(Rs), 32))
COMPFLAG.GT  = (SInt(GPR_val(Rt), 32) > SInt(GPR_val(Rs), 32))
PC = PC + 4
'''],

"fbr":[
r"The \lstinline!FBR! instruction fetches the value of the given comparison flag \code{comp\_flag} and writes it to the destination GPR \code{Rd}. Table~\ref{tab:cmp_flags} lists all allowed comparison flags and the corresponding meaning in eQASM.",
"FBR <comp_flag>, Rd",
'''GPR(Rd) = ZeroExt(CompFlag_val(comp_flag), 32)
PC = PC + 4
'''],

"fmr":[
r"The \lstinline!FMR! instruction fetches the measurement result of the \textbf{last measurement instruction on qubit \code{i}} and writes it to the destination GPR \code{Rd}.",
"FMR Rd, Qi",
'''Wait until the last measurement instruction on qubit \code{i} finishes, i.e., the qubit measurement result register \code{Qi} gets valid, then perform the following:
GPR(Rd) = ToUBitStr(Qi, 32)
PC = PC + 4
'''],

"ldi":[
r"The \lstinline!LDI! instruction loads the signed immediate value \code{Imm20} into the destination GPR \code{Rd}.",
"LDI Rd, Imm20",
'''GPR(Rd) = SignExt(Imm20, 32)
PC = PC + 4
'''],

"ldui":[
r"The \lstinline!LDUI! instruction inserts an 15-bit constant into the upper 15 bits of the destination GPR \code{Rd}.",
"LDUI Rd, Rs, Imm15",
'''GPR(Rd) = Imm15 << 17 | GPR_val(Rs)[16:0]
PC = PC + 4
'''],

"ld":[
r"The \lstinline!LD! instruction loads the word from the memory address specified by the register \code{Rt} with an offset \code{Imm10} into the destination GPR \code{Rd}.",
"LD Rd, Rt(Imm10)",
'''GPR(Rd) = MemWord_val(UInt(GPR_val(Rt), 32) + SignExt(Imm10, 32))
PC = PC + 4
'''],

"st":[
r"The \lstinline!ST! instruction stores the value of GPR \code{Rs} to the memory address specified by the register \code{Rt} with an offset \code{Imm10}.",
"ST Rs, Rt(Imm10)",
'''MemWord(UInt(GPR_val(Rt), 32) + SignExt(Imm10, 32)) = GPR_val(Rs)
PC = PC + 4
'''],

"or":[
r"The \lstinline!OR! instruction performs a bitwise OR of two GPR (\code{Rs}, \code{Rt}) values and writes the result to the destination GPR \code{Rd}.",
"OR Rd, Rs, Rt",
'''GPR(Rd) = GPR_val(Rs) | GPR_val(Rt)
PC = PC + 4
'''],

"and":[
r"The \lstinline!AND! instruction performs a bitwise AND of two GPR (\code{Rs}, \code{Rt}) values and writes the result to the destination GPR \code{Rd}.",
"AND Rd, Rs, Rt",
'''GPR(Rd) = GPR_val(Rs) & GPR_val(Rt)
PC = PC + 4
'''],

"xor":[
r"The \lstinline!XOR! instruction performs a bitwise XOR of two GPR (\code{Rs}, \code{Rt}) values and writes the result to the destination GPR \code{Rd}.",
"XOR Rd, Rs, Rt",
'''GPR(Rd) = GPR_val(Rs) ^ GPR_val(Rt)
PC = PC + 4'''],

"not":[
r"The \lstinline!NOT! instruction performs a bitwise NOT of a GPR (\code{Rt}) value and writes the result to the destination GPR \code{Rd}.",
"NOT Rd, Rt",
'''GPR(Rd) = ~GPR_val(Rt)
PC = PC + 4
'''],

"qwait":[
r"The \lstinline!QWAIT! instruction creates a new timing point with a new timing label which is \code{Imm20} cycles later than the previous timing point.",
"QWAIT Imm20",
'''TimingLabel = TimingLabel + 1
TimingQueue.push(TimingLabel, Imm20)
PC = PC + 4
'''],

"qwaitr":[
r"The \lstinline!QWAITR! instruction creates a new timing point with a new timing label which is $k$ cycles later than the previous timing point. $k$ is an unsigned value specified by the 20 least significant bits of GPR \code{Rs}.",
"QWAITR Rs",
'''TimingLabel = TimingLabel + 1
TimingQueue.push(TimingLabel, GPR_val(Rs)[19:0])
PC = PC + 4
'''],

"smis":[
'''The \lstinline!SMIS! instruction sets the single-qubit quantum operation target register \code{Sd} to the mask which selects all qubits as listed in the set \code{<Qubit List>}.\\
\code{<Qubit List>}  has the following format:\\
\lstinline!{<qubit address>[, <qubit address>]*}!
''',
"SMIS Sd, <Qubit List>",
'''QOTRS(Sd) = Imm7
PC = PC + 4
'''],

"smit":[
'''The \lstinline!SMIT! instruction sets the two-qubit quantum operation target register \code{Td} to the mask which selects all allowed qubit pairs as listed in the set \code{<Qubit Pair List>}.\\
\code{<Qubit Pair List>}  has the following format:\\
\lstinline!{(<source qubit address>, <target qubit address>)[, <qubit pair address>]*}!
''',
"SMIT Td, <Qubit Pair List>",
'''QOTRT(Td) = Imm16
PC = PC + 4
'''],

}

# for key, item in op_dict.items():
#     print(key, len(item))

# boolean Condition(cond):
# # return true is the condition holds
#     case cond[3:1]:
#         when '000' result = 0;                          # always or never
#         when "001" result = not ExeFlag.X or ExeFlag.Y; # equal or not equal
#         when "010" result = 1;                          # no significance
#         when "011" result = ExeFlag.Z;                  # ltz or gez
#         when "100" result = ExeFlag.X;                  # ltu or geu
#         when "101" result = ExeFlag.Y;                  # leu or gtu
#         when "110" result = ExeFlag.X xor ExeFlag.Z;    # lt or ge
#         when "111" result = ExeFlag.Y xor ExeFlag.Z;    # le or gt

#     if cond[0] == 0:
#         result = !result

#     return result

# setExeFlagA(Rs, Rt):
#     ExeFlag.X = UInt(Rs, 32) >= UInt(Rt, 32);
#     ExeFlag.Y = UInt(Rs, 32) > UInt(Rt, 32);
#     ExeFlag.Z = Rs[31] xor Rt[31]

# setExeFlagB(Rs, Rt):
#     integer unsigned_sum = UInt(Rs, 32) + UInt(Rt, 32)
#     ExeFlag.X = unsigned_sum[32]        # get the carry out bit
#     ExeFlag.Y = Rs != 0;
#     ExeFlag.Z = Rs[31]


# integer UInt(bit(N) x):
#     result = 0;
#     for i = 1 to N-1:
#         if x[i] = '1':
#             result = result + 2^i

