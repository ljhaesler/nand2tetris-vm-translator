import sys
import logging
import os

# there are 8 segments, each potentially handling a push and a pop command
# this means that writePushPop has 16 different instruction sets
# and there are 8 arithmetic operations
# meaning writeArithmetic has 8 different instruction sets
# if we want efficiency, we can explore which parts of these instruction sets
# overlap with eachother
# but fundamentally, the most readable implementation is to handle each
# possibility 1:1. 
# I will simply write each instruction set to its own .asm file

SEGMENTS = ["local", "argument", "this", "that",
            "pointer", "temp", "static", "constant"]

ARITHMETIC_OPS = ["add", "sub", "neg",
                  "eq", "gt", "lt",
                  "and", "or", "not"]

# eq, gt and lt each jump to a label, and every label in the .asm file must be
# unique -> we count how many of each we've written
CONDITIONAL_OP_COUNTS = {"eq": 0, "gt": 0, "lt": 0}

logger = logging.getLogger(__name__)

class CodeWriter:
    # The API described for this project uses this class to write to a file
    # step-by-step. I won't be using the CodeWriter this way.
    # Instead, it will simply return strings that are saved to a list
    # And then written to a file at the end -> same logic as the assembler
    # Otherwise, if an error is encountered by the parser, the file will
    # be left half-written, or some logic would have to delete the file.

    def __init__(self):
        # used to keep track of label/function context
        self.currentFunction = None

    def _readInstructionSet(self, name, folder):
        instruction_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "instruction_sets", folder)

        logger.info(f"{folder} reading from {instruction_dir}")
        path = os.path.join(instruction_dir, f"{name}.asm")
        with open(path) as file:
            return file.read()

    def _getTempAddress(self, index):
        # temp is RAM[5-12] -> temp 0 is RAM[5], temp 7 is RAM[12]
        if index < 0 or index > 7:
            logger.error(f"temp {index} is out of range (0-7), exiting.")
            sys.exit(1)

        return 5 + index

    def _getPointerAddress(self, index):
        # pointer 0 is THIS, pointer 1 is THAT
        if index == 0:
            return "THIS"
        if index == 1:
            return "THAT"

        logger.error(f"pointer {index} is out of range (0-1), exiting.")
        sys.exit(1)

    def writeArithmetic(self, command):
        if command not in ARITHMETIC_OPS:
            logger.error(f"{command} is not a valid arithmetic command, exiting.")
            sys.exit(1)

        instructions = self._readInstructionSet(command, "arithmetic")

        if command in CONDITIONAL_OP_COUNTS:
            # fills in %(qty)s, e.g. (EQ_TRUE_%(qty)s) -> (EQ_TRUE_0)
            instructions = instructions % {"qty": CONDITIONAL_OP_COUNTS[command]}
            CONDITIONAL_OP_COUNTS[command] += 1

        return instructions

    def writePushPop(self, command, segment, index, filename=None):
        if command != "push" and command != "pop":
            logger.error(f"{command} is not a valid push/pop command, exiting.")
            sys.exit(1)

        if segment not in SEGMENTS:
            logger.error(f"{segment} is not a valid memory segment, exiting.")
            sys.exit(1)

        if command == "pop" and segment == "constant":
            logger.error("pop constant is not a valid command, exiting.")
            sys.exit(1)

        if segment == "static" and filename == None:
            logger.error("push/pop on static segment requires a filename, exiting.")
            sys.exit(1)

        instructions = self._readInstructionSet(f"{command}_{segment}", "pushpop")

        # each segment's instruction set needs different values filled in
        if segment == "temp":
            values = {"address": self._getTempAddress(index)}
        elif segment == "pointer":
            values = {"address": self._getPointerAddress(index)}
        elif segment == "static":
            values = {"filename": filename, "index": index}
        else:
            # local, argument, this, that, constant
            values = {"index": index}

        return instructions % values

    def writeLabel(self, label):
        instructions = self._readInstructionSet("label", "branching")
        values = {"label": label, "function": ""}

        if self.currentFunction:
            values["function"] = self.currentFunction

        return instructions % values

    def writeGoto(self, label):
        instructions = self._readInstructionSet("goto", "branching")
        values = {"label": label, "function": ""}

        if self.currentFunction:
            values["function"] = self.currentFunction

        return instructions % values

    def writeIf(self, label):
        instructions = self._readInstructionSet("if-goto", "branching")
        values = {"label": label, "function": ""}

        if self.currentFunction:
            values["function"] = self.currentFunction

        return instructions % values
