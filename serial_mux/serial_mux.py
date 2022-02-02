from time import sleep
from typing import BinaryIO

from .control import Control


def serial_mux(handle: BinaryIO, log_handle: BinaryIO, device: str) -> None:
    """Serial multiplexer.

    :arg handle: Output file.
    :arg log_handle: Log file.
    :arg device: Device name.
    """
    muxs = Control(device, log_handle).init()

    handle.write('Virtual ports detected: {}\n'.format(len(muxs)))
    for mux in muxs:
        handle.write('  Mux{}: {}\n'.format(mux.id, mux.name))

    while True:
        if not any([mux.update() for mux in muxs]):
            sleep(0.01)
