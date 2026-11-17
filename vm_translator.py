import logging
import argparse
import vm_parser
import os


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

parser = vm_parser.Parser(args.filename)

logger.info("Preparing file to write to")
writeFileName = os.path.basename(args.filename).removesuffix(".vm") + ".asm"

outputDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "translated")
os.makedirs(outputDir, exist_ok=True)
with open(os.path.join(outputDir, writeFileName), "w") as file:
    exit()
