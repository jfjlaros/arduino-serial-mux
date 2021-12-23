from io import BlockingIOError
from os import openpty, read, set_blocking, ttyname, write
from serial import serial_for_url
from sys import stderr
from time import sleep, time
from tty import setcbreak



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


def serialmux(name, number):
    """"""
    connection = serial_for_url(name)

    muxs = []
    for i in range(1, number + 1):
        muxs.append(Mux(connection, i, stderr))
        print('mux {} is on {}'.format(muxs[-1].id, muxs[-1].name))

    while True:
        for mux in muxs:
            mux.update()
        sleep(0.001)


def main():
    """Main entry point."""
    serialmux('/dev/ttyUSB0', 2)


if __name__ == '__main__':
    main()
