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
# possibility 1:1. I might even write each instruction set to its own .asm file

SEGMENTS = ["local", "argument", "this", "that",
            "pointer", "temp", "static", "constant"]

ARITHMETIC_OPS = ["add", "sub", "neg",
                  "eq", "gt", "lt",
                  "and", "or", "not"]

# eq, gt and lt each jump to a label, and every label in the .asm file must be
# unique -> we count how many of each we've written
CONDITIONAL_OP_COUNTS = {"eq": 0, "gt": 0, "lt": 0}

INSTRUCTION_SETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "instruction_sets")

logger = logging.getLogger(__name__)

class CodeWriter:
    # The API described for this project uses this class to write to a file
    # step-by-step. I won't be using the CodeWriter this way.
    # Instead, it will simply return strings that are saved to a list
    # And then written to a file at the end -> same logic as the assembler
    # Otherwise, if an error is encountered by the parser, the file will
    # be left half-written, or some logic would have to delete the file.
    # -> no __init__ is needed

    def _readInstructionSet(self, name):
        # e.g. name="add" reads instruction_sets/add.asm
        path = os.path.join(INSTRUCTION_SETS_DIR, f"{name}.asm")
        with open(path) as file:
            return file.read()


    def writeArithmetic(self, command):
        if command not in ARITHMETIC_OPS:
            logger.error(f"{command} is not a valid arithmetic command, exiting.")
            sys.exit(1)

        instructions = self._readInstructionSet(command)

        if command in CONDITIONAL_OP_COUNTS:
            # fills in %(qty)s, e.g. (EQ_TRUE_%(qty)s) -> (EQ_TRUE_0)
            instructions = instructions % {"qty": CONDITIONAL_OP_COUNTS[command]}
            CONDITIONAL_OP_COUNTS[command] += 1

        return instructions

    def writePushPop(self, command, segment, index):
        if command == "pop":

        if command == "push":
            sp = self._incrementStackPointer()

        if not sp:
            logger.error(f"{command} is not a valid push/pop command, exiting.")
            sys.exit(1)

        # the instructions change quite a lot between segments
        # I will use helper functions here
        if segment in SEGMENTS:



