from io import BytesIO


class Serial():
    def __init__(self: object, data: bytes) -> None:
        self._rx = BytesIO(data);
        self._tx = BytesIO();

    def read(self: object, size: int=1) -> bytes:
        return self._rx.read(size);

    def write(self: object, data: bytes) -> int:
        return self._tx.write(data)

    def prepare(self: object, data: bytes) -> None:
        self._rx.write(data)
        self._rx.seek(self._rx.tell() - len(data))

    def inspect(self: object, size: int=1) -> bytes:
        self._tx.seek(self._tx.tell() - size)
        return self._tx.read(size)


def serial_for_url(*args, **kwargs) -> object:
    return Serial(b'serialMux\x02\x00\x00\x02\x00')
