import logging
import argparse
import vm_parser
import vm_code_writer
import os
import sys


argparser = argparse.ArgumentParser(
    prog='Hack Virtual Machine Translator',
    description='Takes a .vm file, or a folder of .vm files, ' +
                'and converts it into a single .asm file')

argparser.add_argument('source', help='a .vm file, or a folder of .vm files')
argparser.add_argument('-v', '--verbose', action='store_true',
                       help='show INFO-level parsing details')

args=argparser.parse_args()

logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                    format='%(name)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

def translateFile(vmPath, codeWriter):
    logger.info(f"Translating {vmPath}")

    with open(vmPath) as file:
        parser = vm_parser.Parser(file.readlines())

    # e.g. "path/to/Ball.vm" -> "Ball"
    # names the static variables (@Ball.0, @Ball.1, ...)
    codeWriter.setFilename(os.path.basename(vmPath).removesuffix(".vm"))

    instructions = []

    while parser.hasMoreCommands():
        parser.advance()
        commandType = parser.commandType()

        if commandType == "C_ARITHMETIC":
            instructions.append(codeWriter.writeArithmetic(parser.arg1()))
        elif commandType == "C_PUSH":
            instructions.append(codeWriter.writePushPop("push", parser.arg1(),
                                                        parser.arg2()))
        elif commandType == "C_POP":
            instructions.append(codeWriter.writePushPop("pop", parser.arg1(),
                                                        parser.arg2()))
        elif commandType == "C_LABEL":
            instructions.append(codeWriter.writeLabel(parser.arg1()))
        elif commandType == "C_GOTO":
            instructions.append(codeWriter.writeGoto(parser.arg1()))
        elif commandType == "C_IF":
            instructions.append(codeWriter.writeIf(parser.arg1()))
        elif commandType == "C_FUNCTION":
            instructions.append(codeWriter.writeFunction(parser.arg1(),
                                                         parser.arg2()))
        elif commandType == "C_CALL":
            instructions.append(codeWriter.writeCall(parser.arg1(),
                                                     parser.arg2()))
        elif commandType == "C_RETURN":
            instructions.append(codeWriter.writeReturn())
        else:
            logger.error(f"{parser.currentcommand} is not a recognised command,"
                        + " exiting.")
            sys.exit(1)

    return instructions

codeWriter = vm_code_writer.CodeWriter()
instructions = []

sourcePath = os.path.normpath(args.source)

vmFiles = None

if os.path.isdir(sourcePath): # is the source a directory?
    vmFiles = [name for name in os.listdir(sourcePath)
                     if name.endswith(".vm")]
    if "Sys.vm" not in vmFiles:
        logger.error("No Sys.vm file found in this directory, point to the .vm"
                    + " file directly instead, exiting.")
        sys.exit(1)

    vmFiles = [os.path.join(sourcePath, name) for name in vmFiles]

    # bootstrap is only needed if the source is a directory
    instructions.append(codeWriter.writeInit())

elif sourcePath.endswith(".vm"):
    vmFiles = [sourcePath] # array of length 1, there's only 1 .vm file

else:
    logger.error("Input is neither a .vm file nor a folder, exiting.")
    sys.exit(1)

for vmFile in vmFiles:
    # translateFile returns a list, so use .extend
    instructions.extend(translateFile(vmFile, codeWriter))

# If multiple .vm files, they all need to be written to a single .asm file
logger.info("Preparing file to write to")
fileName = os.path.basename(sourcePath).removesuffix(".vm") + ".asm"
outputDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "translated")
os.makedirs(outputDir, exist_ok=True)

writePath = os.path.join(outputDir, fileName)

with open(writePath, "w") as file:
    file.write("".join(instructions))

logger.info(f"Wrote {len(instructions)} translated commands to {writePath}")
