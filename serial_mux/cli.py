from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType
from sys import stdout

from . import doc_split, usage, version
from .serial_mux import serial_mux


def _arg_parser() -> object:
    """Command line argument parsing."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=usage[0], epilog=usage[1])
    parser.add_argument(
        '-v', action='version', version=version(parser.prog))
    parser.add_argument('device', metavar='DEVICE', type=str, help='device')

    return parser


def main():
    """Main entry point."""
    parser = _arg_parser()

    try:
        args = parser.parse_args()
    except IOError as error:
        parser.error(error)

    serial_mux(stdout, None, args.device)


if __name__ == '__main__':
    main()
