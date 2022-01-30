from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType
from time import sleep
from typing import BinaryIO
from serial import Serial
from struct import pack


def demo(handle: BinaryIO, device: str) -> None:
    """Run a simple ping loop.

    :arg handle: Output file.
    :arg device: Device name.
    """
    interface = Serial(device)

    while True:
        for i in range(256):
            interface.write(pack('B', i));
            sleep(1);
            handle.write(interface.read(interface.in_waiting).decode())
            sleep(1);


def main() -> None:
    """Main entry point."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'device', metavar='DEVICE', type=str, help='device')
    parser.add_argument(
        '-o', dest='handle', metavar='OUTPUT', type=FileType('w'),
        default='-', help='output file')

    try:
        args = parser.parse_args()
    except IOError as error:
        parser.error(error)

    demo(args.handle, args.device)


if __name__ == '__main__':
    main()
