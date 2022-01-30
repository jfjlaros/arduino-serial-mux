from os import openpty, read, set_blocking, ttyname, write
from serial import serial_for_url
from time import sleep, time
from tty import setcbreak
from typing import BinaryIO


_commands = {
    'get_ports': 0,
    'enable': 1,
    'disable': 2,
    'reset': 3}


class SerialMux():
    """Serial multiplexer."""
    _lock = 0

    def __init__(
            self: object, serial: object, id: int, log: BinaryIO=None
            ) -> None:
        """
        :arg serial: Open serial connection.
        :arg id: Mux id.
        :arg log: Open writeable handle to a log file.
        """
        self._serial = serial
        self.id = id
        self._log = log

        self._master, self._slave = openpty()
        self.name = ttyname(self._slave)

        set_blocking(self._master, False)
        setcbreak(self._master)

        self._time = time()

    def _msg(self: object, out: bool, data: bytes) -> None:
        if self._log:
            self._log.write('{:012.2f} {} {} {} ({})\n'.format(
                time() - self._time,
                '<--' if out else '-->',
                self.id,
                ' '.join(list(map(lambda x: '{:02x}'.format(x), data))),
                len(data)))
            self._log.flush()

    def _read(self: object) -> bytes:
        """Read incoming data.

        :returns: The first byte of incoming data.
        """
        if self._serial.in_waiting:
            if not SerialMux._lock:
                SerialMux._lock = ord(self._serial.read(1))
            if SerialMux._lock == self.id:
                SerialMux._lock = 0

                data = self._serial.read(ord(self._serial.read(1)))
                self._msg(False, data)
                return data
        return b''

    def _write(self: object, data: bytes) -> None:
        """Write outgoing data.

        :arg data: Data.
        """
        self._msg(True, data)
        self._serial.write(bytes([self.id, len(data)]) + data)

    def update(self: object) -> None:
        """Perform pending read and write operations."""
        write(self._master, self._read())

        data = b''
        while True:
            try:
                data += read(self._master, 1)
            except BlockingIOError:
                break

        if data:
            self._write(data)


def _control(serial: object, cmd: str) -> int:
    """Send a control comand.

    :arg serial: Open serial connection.
    :arg cmd: Command.

    :returns: Resonse of control command.
    """
    serial.write(bytes([0, 1, _commands[cmd]]))

    if ord(serial.read()):
        raise IOError('Invalid control response.')
    if ord(serial.read()) != 1:
        raise IOError('Invalid control response.')

    return ord(serial.read())


def serial_mux(handle: BinaryIO, log_handle: BinaryIO, device: str) -> None:
    """Serial multiplexer.

    :arg handle: Output file.
    :arg log_handle: Log file.
    :arg device: Device name.
    """
    connection = serial_for_url(device)
    sleep(2)

    number_of_ports = _control(connection, 'get_ports')
    handle.write('Virtual ports detected: {}\n'.format(number_of_ports))

    muxs = []
    for i in range(1, number_of_ports + 1):
        muxs.append(SerialMux(connection, i, log_handle))
        handle.write('  Mux{}: {}\n'.format(muxs[-1].id, muxs[-1].name))

    _control(connection, 'enable')

    while True:
        for mux in muxs:
            mux.update()
        sleep(0.001)
