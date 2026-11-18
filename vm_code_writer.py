import sys
import logging
import os

OPERATIONS = {"add": "@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M",
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
                        f"@{command.upper()}_TRUE_{OPERATIONS[command]}\n"
                        "D;JEQ\n@SP\nA=M-1\nM=0\n"
                        f"({command.upper()}_TRUE_{OPERATIONS[command]})")

        OPERATIONS[command] += 1
        return instructions


    def writeArithmetic(self, command):
        if command in OPERATIONS:
            if command == "eq" or command == "lt" or command == "gt":
                return self._getConditionalOp(command) + f" // {command}"
            return OPERATIONS[command] + f" // {command}"

        logger.error(f"{command} is not a valid arithmetic command")
        sys.exit(1)

