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

ARITHMETIC_OPS = {"add": "@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M",
                "sub": "@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D",
                "and": "@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M",
                "or":  "@SP\nAM=M-1\nD=M\nA=A-1\nM=M|D",
                "neg": "@SP\nA=M-1\nM=-M",
                "not": "@SP\nA=M-1\nM=!M",
                "eq":  0,
                "lt":  0,
                "gt":  0}
              # eq, lt, gt, handled by a helper function:
              # we need to count their quantities.

logger = logging.getLogger(__name__)

class CodeWriter:
    # The API described for this project uses this class to write to a file
    # step-by-step. I won't be using the CodeWriter this way.
    # Instead, it will simply return strings that are saved to a list
    # And then written to a file at the end -> same logic as the assembler
    # Otherwise, if an error is encountered by the parser, the file will
    # be left half-written, or some logic would have to delete the file.
    # -> no __init__ is needed

    def _getConditionalOp(self, command):
        instructions = ("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\nM=-1\n"
                        f"@{command.upper()}_TRUE_{ARITHMETIC_OPS[command]}\n"
                        "D;JEQ\n@SP\nA=M-1\nM=0\n"
                        f"({command.upper()}_TRUE_{ARITHMETIC_OPS[command]})")

        ARITHMETIC_OPS[command] += 1
        return instructions


    def writeArithmetic(self, command):
        if command in ARITHMETIC_OPS:
            if command == "eq" or command == "lt" or command == "gt":
                return self._getConditionalOp(command) + f" // {command}\n"
            return ARITHMETIC_OPS[command] + f" // {command}\n"

        logger.error(f"{command} is not a valid arithmetic command, exiting.")
        sys.exit(1)

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



