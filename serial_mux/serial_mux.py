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
    _id = 0

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

    def _raw_read(self: object) -> bytes:
        """Read from master serial device.

        :returns: Data.
        """
        data = self._serial.read()
        if self._log:
            self._log.write('{:012.2f} --> {:02x} ({})\n'.format(
                time() - self._time, ord(data), data))
        return data

    def _raw_write(self: object, data: bytes) -> None:
        """Write to master serial device.

        :arg data: Data.
        """
        if self._log:
            self._log.write('{:012.2f} <-- {:02x} ({})\n'.format(
                time() - self._time, ord(data), data))
        self._serial.write(data)

    def _available(self: object) -> int:
        """Get the number of bytes available for reading.

        :returns: Number of bytes.
        """
        if not SerialMux._id and self._serial.in_waiting:
            SerialMux._id = ord(self._raw_read())
        if SerialMux._id == self.id:
            return 1
        return 0

    def _read(self: object) -> bytes:
        """Read incoming data.

        :returns: The first byte of incoming data.
        """
        SerialMux._id = 0
        return self._raw_read()

    def _write(self: object, data: bytes) -> None:
        """Write outgoing data.

        :arg data: Data.
        """
        self._raw_write(bytes([self.id]))
        self._raw_write(data)

    def update(self: object) -> None:
        """Perform pending read and write operations."""
        if self._available():
            write(self._master, self._read())

        try:
            data = read(self._master, 1)
        except BlockingIOError:
            return
        self._write(data)


def _control(serial: object, cmd: str) -> int:
    """Send a control comand.

    :arg serial: Open serial connection.
    :arg cmd: Command.

    :returns: Resonse of control command.
    """
    serial.write(bytes([0, _commands[cmd]]))

    if ord(serial.read()):
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
