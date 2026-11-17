import sys
import logging
import os

logger = logging.getLogger(__name__)

class CodeWriter:
    # The API described for this project uses this class to write to a file
    # step-by-step. I won't be using the CodeWriter this way.
    # Instead, it will simply return strings that are saved to a list
    # And then written to a file at the end -> same logic as the assembler
    # Otherwise, if an error is encountered by the parser, the file will
    # be left half-written, or some logic would have to delete the file.
    # -> no __init__ is needed

    def writeArithmetic(self, command):
        pass
