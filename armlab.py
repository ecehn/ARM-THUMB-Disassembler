instruction_bytes = []
with open("arm_thumb_instructions.bin", 'rb') as inst_file:
    instr_str = inst_file.readlines()[0]
for byte in bytearray(instr_str):
    instruction_bytes.append(byte)
""" BEGIN SOLUTION """

'''
Instruction Groups:
- Branch and Control
- Data processing
- Reg load and store
- Status register access
- Coprocessor
'''

instr_as_bin = []
instr_as_hex = []
instr_bin2 = []
print(instruction_bytes)
def to_binary(byte):
  counter = 0
  zeroFill = ""
  for byte in instruction_bytes:
    instr_as_hex.append(hex(byte))
    for x in range(10-len(bin(byte))):
      zeroFill += '0'
    instr_as_bin.append(zeroFill + bin(byte)[2:])
    zeroFill = ""

  for y in range(0, len(instr_as_bin) - 1, 2):
    instr_bin2.append(instr_as_bin[y] + instr_as_bin[y+1])

to_binary(instruction_bytes)
print(instr_as_bin)
print(instr_bin2)



""" END SOLUTION """

MSR = {0:"LSL", 1:"LSR", 2:"ASR"}
ADDSUB = {0:"ADD", 1:"SUB"}
MCASI = {0:"MOVS", 1:"CMP", 2:"ADDS", 3:"SUBS"}
ALU = {0:"AND", 1:"EOR", 2:"LSL", 3:"LSR", 4:"ASR", 5:"ADC", 6:"SBC", 7:"ROR", 8:"TST", 
       9:"NEG", 10:"CMP", 11:"CMN", 12:"ORR", 13:"MUL", 14:"BIC", 15:"MVN"}
HIREG = {0:"ADD", 1:"CMP", 2:"MOV", 3:"BX"}
LSBWFLAG = {"00":"STR", "01":"STRB", "10":"LDR", "11":"LDRB"}
SEHFLAG = {"00":"STRH", "01":"LDRH", "10":"LDSB", "11":"LDSH"}
CONDBRANCH = {"0000":"BEQ", "0001":"BNE", "0010":"BCS", "0011":"BCC", "0100":"BMI", "0101":"BPL", "0110":"BVS",
              "0111":"BVC", "1000":"BHI", "1001":"BLS", "1010":"BGE", "1011":"BLT", "1100":"BGT", "1101":"BLE",}


def machine_to_assembly(instruction):
    """ BEGIN SOLUTION """
    assembly = []
    conditionCode = int(instruction[0:3], 2)
    rs = "R" + str(int(instruction[10:13],2))
    rd = "R" + str(int(instruction[13:16],2))

    # Move shifted register, ADD/SUB
    if conditionCode == 0:
      opCode = int(instruction[3:5], 2)
      if opCode != 3:
        op = MSR[opCode]
        offset5 = "#" + str(int(instruction[5:10],2))
        assembly = [op, rd, rs, offset5]
      elif opCode == 3:
        iFlag = int(instruction[5])
        op = ADDSUB[int(instruction[6])]
        rnOffset = int(instruction[7:10], 2)
        assembly = [op, rd, rs, (("#" + str(rnOffset)) if iFlag == 1 else ("R" + str(rnOffset)))]

    # Move/compare/add/subtract immediate
    elif conditionCode == 1:
      rd_alt = "R" + str(int(instruction[5:8], 2))
      offset8 = str(int(instruction[8:16],2))
      assembly = [MCASI[int(instruction[3:5], 2)], rd_alt, "#" + str(int(instruction[8:16],2))]

    # ALU operations ~ Load/store sign extended
    elif conditionCode == 2:
      # ALU operations
      if int(instruction[3:6], 2) == 0:
        assembly = [ALU[int(instruction[6:10], 2)], rd, rs]

      # Hi register operations
      elif int(instruction[3:6], 2) == 1:
        h1 = int(instruction[8])
        h2 = int(instruction[9])
        assembly = [HIREG[int(instruction[6:8], 2)], ("R" + str(int(instruction[13:16],2))) if h1 == 0 else ("H" + str(8 + int(instruction[13:16],2))), 
                    ("R" + str(int(instruction[10:13],2))) if h2 == 0 else ("H" + str(8 + int(instruction[10:13],2))) if (int(instruction[6:8], 2) != 3) else 
                    ("R" + str(int(instruction[10:13],2))) if h2 == 0 else ("H" + str(8 + int(instruction[10:13],2)))]

      # PC Relative Load
      elif int(instruction[3:5], 2) == 1:
        assembly = ["LDR", "R" + str(int(instruction[5:8], 2)), "[PC, #" + str(int(instruction[8:16], 2) << 2) + "]"]

      # Load/store with register offset
      elif int(instruction[3]) == 1 and int(instruction[6]) == 0:
        LB = str(int(instruction[4])) + str(int(instruction[5]))
        ro = 'R' + str(int(instruction[7:10], 2))
        assembly = [LSBWFLAG[LB], rd, '[' + rs + ',' + ro + ']']

      # Load/store sign extended
      elif int(instruction[3]) == 1 and int(instruction[6]) == 1:
        SH = str(int(instruction[5])) + str(int(instruction[4]))
        ro = 'R' + str(int(instruction[7:10], 2))
        assembly = [SEHFLAG[SH], rd, '[' + rs + ',' + ro + ']']

    # Load store with immediate offset    
    elif conditionCode == 3:
      LB = str(int(instruction[4])) + str(int(instruction[3]))
      offset5 = str(int(instruction[5:10], 2) << 2)
      assembly = [LSBWFLAG[LB], rd, '[' + rs + ',' + '#' + offset5 + ']']

    # Load/store halfword and SP-relative load/store
    elif conditionCode == 4:

      # Load/Store halfword
      if int(instruction[3]) == 0:
        offset5 = str(int(instruction[5:10], 2) << 1)
        assembly = [('STRH' if int(instruction[4]) == 0 else 'LDRH'), rd, '[' + rs + ', #' + offset5 + ']']
      # SP Relative load/store
      elif int(instruction[3]) == 1:
        rd_alt = 'R' + str(int(instruction[5:8], 2))
        word8 = str(int(instruction[8:16], 2) << 2)
        assembly = [('STR' if int(instruction[4]) == 0 else 'LDR'), rd_alt, '[SP, ' + ' #' + word8 + ']']
   
    # Load Addr
    elif conditionCode == 5:

      # Load address
      if int(instruction[3]) == 0:
        rd_alt = 'R' + str(int(instruction[5:8], 2))
        word8 = str(int(instruction[8:16], 2) << 2)
        assembly = ['ADD ', rd_alt, ('PC' if int(instruction[4]) == 0 else 'SP'), '#' + word8 ]
    
    # Software interrupt
    elif conditionCode == 6:
      if int(instruction[4:8], 2) == 15:
        value8 = str(int(instruction[8:16], 2))
        assembly = ['SWI', value8]

    if assembly[0] == '':
      print("Invalid instruction")
    else:
      print(assembly)

    
    """ END SOLUTION """
    
for j in instr_bin2:
  machine_to_assembly(j)
                    
