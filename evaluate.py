from collections import namedtuple
import math
import sys

lmc_parm = {
    "input": 0,
    "neg_flag": False
}

report = {
    "total_fc": 0,
    "total_mailbox": 0,
    "out": ""
}

OPCODES = {
    "ADD": 1,
    "SUB": 2,
    "STO": 3,
    "LDA": 4,
    "BR": 5,
    "BRZ": 6,
    "BRP": 7,
    "IN": 8,
    "OUT": 9,
    "HLT": 0,
    "DAT": None
}

RAM_SIZE = 100
RAM_SIZE_DECLENGTH = math.ceil(math.log(RAM_SIZE, 10))

PRINT_DEBUG = False

# Used in the process of compiling
LabelledCommandTuple = namedtuple(
    "LabelledCommandTuple", ["label", "opcode", "operand"])
CommandTuple = namedtuple("CommandTuple", ["opcode", "operand"])

# An index of labels: name -> address
LABELS_INDEX = {}

def get_label_from_numeric(num):
    for key, value in LABELS_INDEX.items():
        if value == num:
            return key
    raise ValueError("Unknown label {}".format(num))

# For a synatx error in the code
class CompileError(Exception):
    pass

def compile_assembly(asm):
    """
    Compiles the assembly code into the RAM.
    The RAM works using a list.

    1. Split into individual lines
    2. For each line, remove all comments (then remove all empty lines)
    3. Split each into (up to) 3 parts by whitespace. Organise into tuples like:
        (label, opcode, operand)
    4. Everywhere an operand uses a label, replace the label with a numeric value (the memory address of the line with
        that label)
    5. Assemble the commands in their numeric form into the memory.
    @param asm:
    @return:
    """

    memory = [0] * RAM_SIZE

    # STEP 1 - Split code into individual lines
    asm_lines = asm.split("\n")

    # STEP 2a - Remove comments
    for i, line in enumerate(asm_lines):
        code, *comments = line.split("#")   # Part before any hash symbols stays
        asm_lines[i] = code.strip()

    #       b - Remove empty lines
    asm_lines = [line for line in asm_lines if line]

    # Calculate the mailbox usage
    report["total_mailbox"] = len(asm_lines)

    # STEP 3 - Split into command tuples
    labelled_command_tuples = []
    for linenum, line in enumerate(asm_lines, start=1):
        # Remove comments from lines & split by whitespace
        parts = line.split("//")[0].split()

        # If it has 3 parts, they are (label, opcode, operand)
        # If it has 2 parts, they are (label, opcode) or (opcode, operand), depending on which is a valid opcode
        #  (if neither is valid, a CompileError is raised)
        # If it has 1 part, it is an opcode
        # If it has more, raise a CompileError

        if len(parts) == 1:
            # Confirm it is a valid opcode
            if parts[0] not in OPCODES.keys():
                raise CompileError("No valid opcode found on line {} ({})".format(linenum, parts))
            labelled_command_tuples.append(LabelledCommandTuple("", parts[0], 0))

        elif len(parts) == 2:
            first, second = parts

            if first in OPCODES.keys():
                # If it is a valid int, turn it into that
                # This is because string values in the operand section will be treated as labels
                try:
                    second = int(second)
                except ValueError:
                    pass
                labelled_command_tuples.append(LabelledCommandTuple("", first, second))
            elif second in OPCODES.keys():
                labelled_command_tuples.append(LabelledCommandTuple(first, second, 0))
            else:
                raise CompileError("No valid opcode found on line {}".format(linenum))

        elif len(parts) == 3:
            # Confirm the second is a valid opcode
            if parts[1] not in OPCODES.keys():
                raise CompileError("No valid opcode found on line {}".format(linenum))

            # If the operand is a valid int, turn it into that
            try:
                parts[2] = int(parts[2])
            except ValueError:
                pass

            labelled_command_tuples.append(LabelledCommandTuple(parts[0], parts[1], parts[2]))

        elif len(parts) > 3:
            raise CompileError("Too many parts in line {}".format(linenum))

    # STEP 4 - Replace labels with numeric IDs
    for i, command in enumerate(labelled_command_tuples):
        if command.label:
            # Is there already one there?
            if command.label in LABELS_INDEX.keys():
                raise CompileError("Already a line with label {}".format(command.label))

            # There isn't, so add it now
            LABELS_INDEX[command.label] = i

    # Finally, Perform replacements
    command_tuples = []
    for command in labelled_command_tuples:
        if isinstance(command.operand, str):
            if command.operand in LABELS_INDEX.keys():
                label_numeric = LABELS_INDEX[command.operand]
            else:
                raise CompileError("Unknown label: {}".format(command.operand))

            new_command = CommandTuple(command.opcode, label_numeric)
            command_tuples.append(new_command)
        else:
            command_tuples.append(CommandTuple(command.opcode, command.operand))

    # STEP 5 - Assemble numerically
    opcode_mult = 10 ** RAM_SIZE_DECLENGTH

    for i, command in enumerate(command_tuples):
        if command.opcode == "DAT":
            # DAT just places the command in the box
            memory[i] = command.operand
            continue

        numeric_opcode = OPCODES[command.opcode]

        memory[i] = (numeric_opcode * opcode_mult) + command.operand

    return memory

def write_memory(address, content, registers, memory):
    registers["mar"] = address
    registers["mdr"] = content
    memory[registers["mar"]] = registers["mdr"]
    if PRINT_DEBUG: print("Wrote {data} to address {addr} ({name})".format(data=content, addr=address, name=get_label_from_numeric(address)))

def read_memory(address, registers, memory):
    registers["mar"] = address
    registers["mdr"] = memory[registers["mar"]]
    if PRINT_DEBUG: print("Read {data} from address {addr} ({name}) into MDR".format(data=registers["mdr"], addr=address, name=get_label_from_numeric(address)))

def exec_ADD(operand, registers, memory):
    read_memory(operand, registers, memory)     # Read from operand to MDR
    registers["acc"] += registers["mdr"]        # Add MDR to accumulator
    if registers["acc"] > 999:                  # If value above 1000, overflow
        registers["acc"] -= 1000
    if PRINT_DEBUG:
        print("Added MDR to accumulator")

def exec_SUB(operand, registers, memory):
    read_memory(operand, registers, memory)     # Read from operand to MDRs
    registers["acc"] -= registers["mdr"]        # Subtract MDR from accumulator
    if registers["acc"] < 0:                    # If value below 0, downflow and raise the negative flag
        lmc_parm["neg_flag"] = True
        registers["acc"] += 1000
    if PRINT_DEBUG:
        print("Subtracted MDR from accumulator")

def exec_STA(operand, registers, memory):
    write_memory(operand, registers["acc"],
                 registers, memory)             # Write from accumulator to memory
    if PRINT_DEBUG:
        print("Stored accumulator in memory")

def exec_LDA(operand, registers, memory):
    read_memory(operand, registers, memory)     # Read from operand to MDR
    registers["acc"] = registers["mdr"]         # Store MDR in accumulator
    # All data stored in mailboxes should be positive. Load data will reset the negative flag (neg_flag)
    lmc_parm["neg_flag"] = False
    if PRINT_DEBUG:
        print("Loaded MDR into accumulator")

def exec_BRA(operand, registers, memory):
    registers["pc"] = operand                   # Save operand to PC (branch)
    if PRINT_DEBUG: print("Set PC to {addr} ({name})".format(addr=operand, name=get_label_from_numeric(operand)))

def exec_BRZ(operand, registers, memory):
    if registers["acc"] == 0:
        registers["pc"] = operand
        if PRINT_DEBUG: print("Set PC to {} as acc == 0".format(operand))
    else:
        if PRINT_DEBUG: print("No change to PC as ass != 0")


def exec_BRP(operand, registers, memory):
    if registers["acc"] >= 0 and not lmc_parm["neg_flag"]:
        registers["pc"] = operand
        if PRINT_DEBUG: print("Set PC to {} as acc > 0".format(operand))
    else:
        if PRINT_DEBUG: print("No change to PC as ass != 0")

def exec_INP(operand, registers, memory):
    registers["acc"] = lmc_parm["input"]

def exec_OUT(operand, registers, memory):
    print(registers["acc"], end=' ')
    report["out"] += str(registers["acc"]) + " "

EXEC_DICT = {
    1: exec_ADD,
    2: exec_SUB,
    3: exec_STA,
    4: exec_LDA,
    5: exec_BRA,
    6: exec_BRZ,
    7: exec_BRP,
    8: exec_INP,
    9: exec_OUT
}

def execute(memory, pc=0):
    """
    Executes the data in the memory given.
    @param memory:
    @param pc: Program counter
    @return:
    """

    # Registers
    registers = {
        "acc": 0,   # Accumulator
        "cir": 0,   # Current instruction register
        "mdr": 0,   # Memory data register
        "mar": 0,   # Memory address register
        "pc": pc    # Program counter
    }

    while True:
        # Fetch, decode, execute
        # 1. Fetch

        # Move current program counter to MAR
        registers["mar"] = registers["pc"]

        # Increment PC
        registers["pc"] += 1

        # Increment total fetch cycle, will not be reseted till finish
        report["total_fc"] += 1

        # Get memory from address in MAR and store in MDR
        registers["mdr"] = memory[registers["mar"]]

        # Store the instruction in the CIR
        registers["cir"] = registers["mdr"]

        # 2. Decode
        # Find basic opcode number
        opcode = int(math.floor(registers["cir"] / (10**RAM_SIZE_DECLENGTH)))
        operand = registers["cir"] - (opcode * 10**RAM_SIZE_DECLENGTH)

        # 3. Execute
        # Pass of to a dict of functions
        if opcode == 0:
            # HLT operation
            return
        EXEC_DICT[opcode](operand, registers, memory)

def test_bsc(num, zero=True):
    n = num
    res = ""
    while True:
        if n > 999:
            n = 0
            if zero:
                res += str(0)
            break
        if n == 1 or n == 0:
            res += str(n)
            break
        res += str(n) + " "
        if n % 2 == 0:
            n = int(n / 2)
        else:
            n = int(n * 3 + 1)
    return res.strip()

def test_adv(num, zero=True):
    n = num
    res = ""
    while True:
        if n > 999:
            n = 0
            if zero:
                res += str(0)
            break
        if n == 1 or n == 0:
            res += str(n)
            break
        res += str(n) + " "
        if n % 2 == 0:
            n = int(n / 2)
        else:
            n = int((n * 3 + 1) / 2)
    return res.strip()


def main():
    """
    Compile then execute
    @return:
    """
    file_ = sys.argv[1]
    start_index = int(sys.argv[2])

    # Allow single index
    try:
        end_index = int(sys.argv[3])
    except:
        end_index = start_index
    
    task = sys.argv[4]
    zero = sys.argv[5]

    if zero == 'f':
        zero = False
    elif zero == 't':
        zero = True
    else:
        raise


    avg_cycle = 0

    # Open the asm code
    f = open(file_)

    # Read the code into str
    asm = f.read()

    for i in range(start_index, end_index+1):
        # Reset parameters
        global lmc_parm, report, LABELS_INDEX
        lmc_parm = {
            "input": i,
            "neg_flag": False
        }
        report = {
            "total_fc": 0,
            "total_mailbox": 0,
            "out": ""
        }
        LABELS_INDEX = {}

        # Compile the program
        memory = compile_assembly(asm)

        # Run the program
        print("Start at:", i)
        print(">", end = " ")
        execute(memory)
        
        if task == "bsc":
            assert report["out"].strip() == test_bsc(i, zero=zero)
        elif task == "adv":
            assert report["out"].strip() == test_adv(i, zero=zero)

        avg_cycle += report["total_fc"]

        print("\n> fetch-execute cycles:", report["total_fc"], "\n")

    print("All test passed! ")
    print("Total mailboxes used:", report["total_mailbox"])
    print("Average fetch-execute cycles:", int(avg_cycle/(end_index - start_index + 1)))

if __name__ == "__main__":
    main()