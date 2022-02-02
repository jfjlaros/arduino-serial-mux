from os import openpty, read, set_blocking, ttyname, write
from serial import serial_for_url
from time import sleep, time
from tty import setcbreak
from typing import BinaryIO


_protocol = b'serialMux'
_version = (1, 0, 0)
_commands = {
    'protocol': 0,
    'get_ports': 1,
    'enable': 2,
    'disable': 3,
    'reset': 4}


def _assert_protocol(protocol: str) -> None:
    if protocol != _protocol:
        raise IOError('invalid protocol header');


def _assert_version(version: tuple) -> None:
    if version[0] != _version[0] or version[1] > _version[1]:
        raise IOError(
            'version mismatch (device: {}, client: {})'.format(
                '.'.join(map(str, version)),
                '.'.join(map(str, _version))))


class Control():
    """Serial multiplexer control channel."""
    _ids = 0;
    _lock = 0
    _log = None
    _serial = None

    def __init__(self: object, device: str, log: BinaryIO=None) -> None:
        """
        :arg device: Device name.
        :arg log: Open writeable handle to a log file.
        """
        Control._serial = serial_for_url(device)
        Control._log = log

        sleep(2)

    def cmd(self: object, cmd: str) -> bytes:
        """Send a control comand.

        :arg cmd: Command.

        :returns: Resonse of control command.
        """
        Control._serial.write(bytes([0, 1, _commands[cmd]]))

        if Control._serial.read() != b'\x00':
            raise IOError('invalid control response')

        size = ord(Control._serial.read())
        if not size:
            raise IOError('invalid control message size')

        return Control._serial.read(size)

    def init(self: object):
        """
        """
        response = self.cmd('protocol')
        _assert_protocol(response[:-3])
        _assert_version(tuple(response[-3:]))

        number_of_ports = ord(self.cmd('get_ports'))

        muxs = []
        for i in range(1, number_of_ports + 1):
            muxs.append(SerialMux())

        self.cmd('enable')

        return muxs


class SerialMux(Control):
    """Serial multiplexer."""
    def __init__(self: object) -> None:
        SerialMux._ids += 1
        self.id = SerialMux._ids

        self._master, self._slave = openpty()
        self.name = ttyname(self._slave)

        set_blocking(self._master, False)
        setcbreak(self._master)

        self._time = time()

    def _msg(self: object, out: bool, data: bytes) -> None:
        if SerialMux._log:
            SerialMux._log.write('{:012.2f} {} {} {} ({})\n'.format(
                time() - self._time,
                '<--' if out else '-->',
                self.id,
                ' '.join(list(map(lambda x: '{:02x}'.format(x), data))),
                len(data)))
            SerialMux._log.flush()

    def _read(self: object) -> bytes:
        """Read incoming data.

        :returns: The first byte of incoming data.
        """
        if SerialMux._serial.in_waiting:
            if not SerialMux._lock:
                SerialMux._lock = ord(SerialMux._serial.read(1))
            if SerialMux._lock == self.id:
                SerialMux._lock = 0

                data = SerialMux._serial.read(ord(SerialMux._serial.read(1)))
                self._msg(False, data)
                return data
        return b''

    def _write(self: object, data: bytes) -> None:
        """Write outgoing data.

        :arg data: Data.
        """
        self._msg(True, data)
        SerialMux._serial.write(bytes([self.id, len(data)]) + data)

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


def serial_mux(handle: BinaryIO, log_handle: BinaryIO, device: str) -> None:
    """Serial multiplexer.

    :arg handle: Output file.
    :arg log_handle: Log file.
    :arg device: Device name.
    """
    muxs = Control(device, log_handle).init()

    handle.write('Virtual ports detected: {}\n'.format(len(muxs)))
    for mux in muxs:
        handle.write('  Mux{}: {}\n'.format(mux.id, mux.name))

    while True:
        for mux in muxs:
            mux.update()
        sleep(0.001)
