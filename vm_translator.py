import logging
import argparse
import vm_parser
import vm_code_writer
import os
import sys


argparser = argparse.ArgumentParser(
    prog='Hack Virtual Machine Translator',
    description='Takes a .vm file and converts it into a .asm file')

argparser.add_argument('filename')
argparser.add_argument('-v', '--verbose', action='store_true',
                       help='show INFO-level parsing details')

args=argparser.parse_args()

logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                    format='%(name)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

if not args.filename.endswith(".vm"):
    logger.error("Input file is not a .vm file, exiting.")
    sys.exit(1)

with open(args.filename) as file:
    parser = vm_parser.Parser(file.readlines())

codeWriter = vm_code_writer.CodeWriter()

# e.g. "path/to/Ball.vm" -> "Ball"
# names the static variables (@Ball.0, @Ball.1, ...) and the .asm file
vmFileName = os.path.basename(args.filename).removesuffix(".vm")

# every command is translated before the .asm file is opened
# -> an error never leaves a half-written file behind
instructions = []

while parser.hasMoreCommands():
    parser.advance()
    commandType = parser.commandType()

    if commandType == "C_ARITHMETIC":
        instructions.append(codeWriter.writeArithmetic(parser.arg1()))
    elif commandType == "C_PUSH":
        instructions.append(codeWriter.writePushPop("push", parser.arg1(),
                                                    parser.arg2(), vmFileName))
    elif commandType == "C_POP":
        instructions.append(codeWriter.writePushPop("pop", parser.arg1(),
                                                    parser.arg2(), vmFileName))
    else:
        logger.error(f"{parser.currentcommand} is not a recognised command, exiting.")
        sys.exit(1)

logger.info("Preparing file to write to")
writeFileName = vmFileName + ".asm"

outputDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "translated")
os.makedirs(outputDir, exist_ok=True)
writePath = os.path.join(outputDir, writeFileName)

with open(writePath, "w") as file:
    file.write("".join(instructions))

logger.info(f"Wrote {len(instructions)} translated commands to {writePath}")
