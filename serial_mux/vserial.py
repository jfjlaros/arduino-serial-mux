from os import fork, getpid, openpty, read, ttyname, write
from tty import setcbreak


class VSerial():
    """Virtual serial device."""
    def __init__(self: object, mux: object, device_id: int) -> None:
        """
        """
        self._mux = mux
        self._id = device_id

        self._master, self._slave = openpty()
        self.name = ttyname(self._slave)

        setcbreak(self._master)

        pid = fork()
        if pid:
            while True:
                self._update()

    def receive(self: object, data: bytes) -> None:
        """
        """
        write(self._master, data)

    def _update(self: object) -> None:
        """
        """
        self._mux.write(self._id, read(self._master, 32))
