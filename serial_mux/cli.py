from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType

from . import doc_split, usage, version
from .serial_mux import serial_mux


def _arg_parser() -> object:
    """Command line argument parsing."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=usage[0], epilog=usage[1])
    parser.add_argument(
        '-o', dest='handle', metavar='OUTPUT', type=FileType('w'),
        default='-', help='output file')
    parser.add_argument(
        '-l', dest='log_handle', metavar='LOG', type=FileType('w'),
        default=None, help='log file')
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

    try:
        serial_mux(**{k: v for k, v in vars(args).items()
                   if k not in ('func', 'subcommand')})
    except (IOError, ValueError) as error:
        parser.error(error)


if __name__ == '__main__':
    main()
