from io import BlockingIOError
from os import openpty, read, set_blocking, ttyname, write
from serial import serial_for_url
from sys import stderr, stdout
from time import sleep, time
from tty import setcbreak


_commands = {
    'get_ports': 0,
    'enable': 1,
    'disable': 2}


class Mux():
    """"""
    _id = 0

    def __init__(self, serial, id, log=None):
        """"""
        self._serial = serial
        self.id = id
        self._log = log

        self._master, self._slave = openpty()
        self.name = ttyname(self._slave)

        set_blocking(self._master, False)
        setcbreak(self._master)

        self._time = time()

    def _raw_read(self):
        data = self._serial.read()
        if self._log:
            self._log.write('{:012.2f} --> {:02x} ({})\n'.format(
                time() - self._time, ord(data), data))
        return data

    def _raw_write(self, data):
        if self._log:
            self._log.write('{:012.2f} <-- {:02x} ({})\n'.format(
                time() - self._time, ord(data), data))
        self._serial.write(data)

    def _available(self):
        """"""
        if not Mux._id and self._serial.in_waiting:
            Mux._id = ord(self._raw_read())
        if Mux._id == self.id:
            return 1
        return 0

    def _read(self):
        """"""
        Mux._id = 0
        return self._raw_read()

    def _write(self, data):
        """"""
        self._raw_write(bytes([self.id]))
        self._raw_write(data)

    def update(self):
        """"""
        if self._available():
            write(self._master, self._read())

        try:
            data = read(self._master, 1)
        except BlockingIOError:
            return
        self._write(data)


def _control(connection, cmd):
    connection.write(bytes([0, _commands[cmd]]))

    if ord(connection.read()):
        raise IOError('Invalid control response.')

    return ord(connection.read())


def serialmux(handle, log_handle, name):
    """"""
    connection = serial_for_url(name)
    sleep(2)

    number_of_ports = _control(connection, 'get_ports')
    handle.write('Virtual ports detected: {}\n'.format(number_of_ports))

    muxs = []
    for i in range(1, number_of_ports + 1):
        muxs.append(Mux(connection, i, log_handle))
        handle.write('  Mux{}: {}\n'.format(muxs[-1].id, muxs[-1].name))

    _control(connection, 'enable')

    while True:
        for mux in muxs:
            mux.update()
        sleep(0.001)


def main():
    """Main entry point."""
    serialmux(stdout, None, '/dev/ttyUSB0')


if __name__ == '__main__':
    main()
