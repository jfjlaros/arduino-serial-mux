from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType
from time import sleep

from simple_rpc import Interface


def demo(device):
    """"""
    interface = Interface(device, wait=2)

    while True:
        for i in range(256):
            print(interface.inc(i))
            sleep(1);


def main():
    """Main entry point."""
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'device', metavar='DEVICE', type=str, help='device')

    try:
        args = parser.parse_args()
    except IOError as error:
        parser.error(error)

    demo(args.device)


if __name__ == '__main__':
    main()
