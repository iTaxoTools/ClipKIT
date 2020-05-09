import logging
import os.path
import sys

from .modes import TrimmingMode

logger = logging.getLogger(__name__)


def process_args(args):
    """
    Function to process arguments
    This function processes arguments
    subfunctions to trim the input file
    """
    inFile = args.input
    outFile = args.output or f"{inFile}.clipkit"

    # check that input file exists
    if not os.path.isfile(inFile):
        logger.warning("Input file does not exist")
        sys.exit()

    if inFile == outFile:
        logger.warning("Input and output files can't have the same name.")
        sys.exit()

    # assign optional arguments
    mode = TrimmingMode(args.mode) if args.mode else TrimmingMode.gappy
    use_log = args.log or False
    gaps = float(args.gaps) if args.gaps is not None else 0.9
    complement = args.complementary or False

    inFileFormat = args.input_file_format
    outFileFormat = args.output_file_format

    return (
        inFile,
        outFile,
        inFileFormat,
        outFileFormat,
        gaps,
        complement,
        mode,
        use_log,
    )
