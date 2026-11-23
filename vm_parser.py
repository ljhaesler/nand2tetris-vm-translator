import sys
import logging

ARITHMETIC = ["add", "sub", "neg",
              "eq", "gt", "lt",
              "and", "or", "not"]

logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, lines):
        # lines: the raw lines of a .vm file, e.g. from file.readlines()
        logger.info("Parsing file")

        self.commands = self._stripAllLines(lines)
        logger.info(f'File contains {len(self.commands)} lines')


    def _stripAllLines(self, lines):
        commands = []

        for i in range(len(lines)):
            command = lines[i].split("//")[0].strip()
            if len(command) > 0:
                commands.append(command)

        if len(commands) > 0:
            return commands

        logger.error("No commands found in .vm file, exiting.")
        sys.exit(1)

    def hasMoreCommands(self):
        logger.info(f'File has {len(self.commands)} lines left')

        if len(self.commands) > 0:
            return True

        return False;

    def advance(self):
        self.currentcommand = self.commands.pop(0)

    def commandType(self):
        command = None

        if self.currentcommand in ARITHMETIC:
            command = "C_ARITHMETIC"
        elif self.currentcommand.startswith("push"):
            command = "C_PUSH"
        elif self.currentcommand.startswith("pop"):
            command = "C_POP"
        elif self.currentcommand.startswith("label"):
            command = "C_LABEL"
        elif self.currentcommand.startswith("goto"):
            command = "C_GOTO"
        elif self.currentcommand.startswith("if-goto"):
            command = "C_IF"
        elif self.currentcommand.startswith("function"):
            command = "C_FUNCTION"
        elif self.currentcommand == "return":
            command = "C_RETURN"
        elif self.currentcommand.startswith("call"):
            command = "C_CALL"

        logger.info(f'{self.currentcommand} parsed as {command}')

        self.command_type = command
        return command

    def arg1(self):
        arg = None

        if self.command_type == "C_ARITHMETIC":
            arg = self.currentcommand

        elif self.command_type in ("C_PUSH", "C_POP", "C_CALL", "C_FUNCTION", "C_GOTO", "C_LABEL", "C_IF"):
            arg = self.currentcommand.split()[1]

        if not arg == None:
            logger.info(f'{self.currentcommand} arg1: {arg}')
            return arg

        logger.error(f'{self.command_type} is an unhandled arg1 command type, exiting.')
        sys.exit(1)

    def arg2(self):

        arg = None

        if self.command_type in ("C_PUSH", "C_POP", "C_CALL", "C_FUNCTION"):
            arg = int(self.currentcommand.split()[2])

        if not arg == None:
            logger.info(f'{self.currentcommand} arg2: {arg}')
            return arg

        logger.error(f'{self.command_type} is an unhandled arg2 command type, exiting.')
        sys.exit(1)


