import sys
import logging

ARITHMETIC = ["add", "sub", "neg",
              "eq", "gt", "lt",
              "and", "or", "not"]

logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, filename):
        logger.info("Parsing file")

        if filename.endswith(".vm"):
            with open(filename) as file:
                self.commands = self._stripAllLines(file.readlines())
                logger.info(f'File contains {len(self.commands)} lines')
            return self

        logger.error("Input file is not a .vm file, exiting.")
        sys.exit(1)


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
        # the only commands we really recognise
        # for the first part of this project:
        # C_ARITHMETIC, C_PUSH, C_POP

        command = None

        if self.currentcommand in ARITHMETIC:
            command = "C_ARITHMETIC"
        elif self.currentcommand.startswith("push"):
            command = "C_PUSH"
        elif self.currentcommand.startswith("pop"):
            command = "C_POP"

        logger.info(f'{self.currentcommand} parsed as {command}')

        self.command_type = command
        return command

    def arg1(self):
        if self.command_type == "C_ARITHMETIC":
            return self.currentcommand

        return self.currentcommand.split()[1]



    



