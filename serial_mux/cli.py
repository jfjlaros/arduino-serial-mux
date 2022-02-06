from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType
from threading import Thread
from typing import BinaryIO

from . import doc_split, usage, version
from .serial_mux import SerialMux


def serial_mux(
        handle: BinaryIO, log_handle: BinaryIO,
        device: str, baudrate: int, wait: int) -> None:
    """Serial multiplexer service.

    :arg handle: Output handle.
    :arg log_handle: Log handle.
    :arg device: Serial device name.
    :arg baudrate: Baud rate.
    :arg wait: Time in seconds before communication starts.
    """
    mux = SerialMux(device, baudrate, wait, log_handle)
    threads = [Thread(target=mux.update, daemon=True)]
    threads[-1].start()

    handle.write('Detected {} virtual serial ports.\n'.format(
        len(mux.devices)))
    for i, device in enumerate(mux.devices):
        handle.write(
            '  Virtual serial device {}: {}\n'.format(i + 1, device.name))
        threads.append(Thread(target=device.update, daemon=True))
        threads[-1].start()

    handle.write('\nPress Ctrl+C to exit.\n')
    for thread in threads:
        thread.join()


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
        '-b', dest='baudrate', type=int, default=9600, help='baud rate')
    parser.add_argument(
        '-w', dest='wait', type=int, default=2,
        help='time before communication starts')

    parser.add_argument(
        '-v', action='version', version=version(parser.prog))
    parser.add_argument('device', metavar='DEVICE', type=str, help='device')

    return parser


def main() -> None:
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
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
