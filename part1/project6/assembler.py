import sys, os

# C-instruction bits
# 1 1 1 a c1 c2 c3 c4 c5 c6 d1 d2 d3 j1 j2 j3
#---------------------------------------------
# A-instructions bits
# 0 v v v v v v v v v v v v v v
#---------------------------------------------

# comp field values
# a c1 c2 c3 c4 c5 c6
compTable = {
  # Constants
  "0":   "0101010",
  "1":   "0111111",
  "-1":  "0111010",
  # Single operand
  "D":   "0001100",
  "A":   "0110000",
  "M":   "1110000",
  "!D":  "0001101",
  "!A":  "0110001",
  "!M":  "1110001",
  "-D":  "0001111",
  "-A":  "0110011",
  "-M":  "1110011",
  "D+1": "0011111",
  "A+1": "0110111",
  "M+1": "1110111",
  "D-1": "0001110",
  "A-1": "0110010",
  "M-1": "1110010",
  # Binary operations
  "D+A": "0000010",
  "D+M": "1000010",
  "D-A": "0010011",
  "D-M": "1010011",
  "A-D": "0000111",
  "M-D": "1000111",
  "D&A": "0000000",
  "D&M": "1000000",
  "D|A": "0010101",
  "D|M": "1010101",
};

#destination field
# d1 d2 d3
destTable = {
  "null":  "000", # no destination
  "M":   "001",
  "D":   "010",
  "MD":  "011",
  "A":   "100",
  "AM":  "101",
  "AD":  "110",
  "AMD": "111",
};

#jump field
# j1 j2 j3
jumpTable = {
  "null":  "000", # no jump
  "JGT": "001",
  "JEQ": "010",
  "JGE": "011",
  "JLT": "100",
  "JNE": "101",
  "JLE": "110",
  "JMP": "111",
};

# pre-defined symbols used in assembly code
table = {
    "SP":0,
    "LCL":1,
    "ARG":2,
    "THIS":3,
    "THAT":4,
    "SCREEN":16384,
    "KBD":24576
}

# pre-defined Registers 
for i in range(16):
    register = "R" + str(i)
    table[register] = i


def strip(line):
    line = line.split("//")[0]
    return line.strip()

# cursor to new variable
newVar = 16
# add new variable
def addVar(var):

    global newVar
    table[var] = newVar
    newVar+=1
    return table[var]

# translate c expressions to binary
def cTranslate(line):
    translated = line.strip()
    cbin = "111"

    # Split into dest and rest
    if "=" in translated:
        dest, rest = translated.split("=")
    else:
        dest, rest = "null", translated

    # Split rest into comp and jump
    if ";" in rest:
        comp, jump = rest.split(";")
    else:
        comp, jump = rest, "null"

    # Build binary code
    cbin += (
        compTable.get(comp.strip(), "0000000")
        + destTable.get(dest.strip(), "000")
        + jumpTable.get(jump.strip(), "000")
    )
    return cbin + "\n"



# translate a expression to binary
def aTranslate(line):
    symbol = line[1:].strip()
    if symbol.isdigit():
        val = int(symbol)
    else:
        val = table.get(symbol, -1)
        if val == -1:
            val = addVar(symbol)
        else:
            val = table[symbol]
    abin = "0" + bin(val)[2:].zfill(15)
    return abin + "\n"

#python3 assembler.py [file_to_compile.asm] [name_of_compiled_file.hack]
# get file to compile
# Get full path of input file
asm_path = sys.argv[1]

# Get directory, base name, and stem
base_name = os.path.splitext(os.path.basename(asm_path))[0]   
dir_name = os.path.dirname(asm_path)                          
tmp_path = os.path.join(dir_name, base_name + ".tmp")         
hack_path = os.path.join(dir_name, base_name + ".hack")       

# First pass
def firstPass():
    with open(asm_path) as inputFile, open(tmp_path, "w") as outputFile:
        line_curs = 0
        for l in inputFile:
            stripped = strip(l)
            if not stripped:
                continue
            if stripped[0] == "(":
                label = stripped[1:-1]
                table[label] = line_curs
            else:
                outputFile.write(stripped + "\n")
                line_curs += 1


# Second pass
def assemble():
    with open(tmp_path) as inputFile, open(hack_path, "w") as outputFile:
        for l in inputFile:
            if l[0] == "@":
                outputFile.write(aTranslate(l))
            else:
                outputFile.write(cTranslate(l))
    os.remove(tmp_path)


firstPass()
assemble()
