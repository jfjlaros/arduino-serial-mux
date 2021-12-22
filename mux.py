from io import BlockingIOError
from os import openpty, read, set_blocking, ttyname, write
from serial import serial_for_url
from time import sleep


class Mux():
    """"""
    _id = 0

    def __init__(self, serial, id):
        """"""
        self._serial = serial
        self.id = id

        self._master, self._slave = openpty()
        self.name = ttyname(self._slave)

        set_blocking(self._master, False)

    def _available(self):
        """"""
        if not Mux._id and self._serial.in_waiting:
            Mux._id = ord(self._serial.read())
        if Mux._id == self.id:
            return 1
        return 0

    def _read(self):
        """"""
        Mux._id = 0
        return self._serial.read()

    def _write(self, data):
        """"""
        self._serial.write(bytes([self.id]) + data)

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
        muxs.append(Mux(connection, i))
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
