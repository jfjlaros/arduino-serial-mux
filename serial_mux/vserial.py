from os import getpid, openpty, read, ttyname, write
from tty import setcbreak


class VSerial():
    """Virtual serial device."""
    def __init__(self: object, mux: object, port: int) -> None:
        """
        :arg mux: Serial multiplexer.
        :arg port: Virtual serial port.
        """
        self._mux = mux
        self._port = port

        self._master, self._slave = openpty()
        setcbreak(self._master)
        self.name = ttyname(self._slave)

    def receive(self: object, data: bytes) -> None:
        """Receive serial data.

        :arg data: Data.
        """
        write(self._master, data)

    def update(self: object) -> None:
        """Send serial data."""
        while True:
            self._update()

    def _update(self: object) -> None:
        """Send serial data."""
        self._mux.send(self._port, read(self._master, 32))
