class Buffer():
    """Ring buffer."""
    def __init__(self: object, size: int=64) -> None:
        """
        :arg size: Buffer size.
        """
        self._start = 0
        self._end = 0
        self._buffer = bytearray(size)

    def available(self: object) -> int:
        """
        Get the number of bytes available for reading.

        :returns: Number of bytes.
        """
        return (self._end - self._start) % len(self._buffer)

    def read(self: object, size: int=1) -> bytes:
        """
        Read `size` bytes of data.

        :arg size: Number of bytes to read.

        :returns: Data.
        """
        data = [] 
        for _ in range(min(size, self.available())):
            data.append(self._buffer[self._start])
            self._start = (self._start + 1) % len(self._buffer)
        return bytes(data)

    def write(self: object, data: bytes) -> None:
        """
        Write data.

        :arg data: Data.
        """
        for byte in data:
            self._buffer[self._end] = byte
            self._end = (self._end + 1) % len(self._buffer)

    def peek(self: object) -> int:
        """
        Return the next byte of incoming data without removing it from the
        buffer.

        :returns: The first byte of incoming data or `-1` if no data is
          available.
        """
        if (self._start != self._end):
            return self._buffer[self._start]
        return -1
