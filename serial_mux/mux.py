from os import openpty, read, set_blocking, ttyname, write
from tty import setcbreak


class SerialMux():
    """Serial multiplexer."""
    def __init__(self: object, control: object) -> None:
        """
        """
        self._control = control
        self.id = self._control.add()

        self._master, self._slave = openpty()
        self.name = ttyname(self._slave)

        set_blocking(self._master, False)
        setcbreak(self._master)

    def update(self: object) -> bool:
        """Perform pending read and write operations."""
        write(self._master, self._control.read(self.id))

        data = b''
        while True:
            try:
                data += read(self._master, 1)
            except BlockingIOError:
                break
        if data:
            self._control.write(self.id, data)
            return True

        return False
