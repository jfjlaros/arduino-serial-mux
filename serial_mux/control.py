from serial import serial_for_url
from time import sleep, time
from typing import BinaryIO

from .mux import SerialMux


_protocol = b'serialMux'
_version = (1, 0, 0)
_commands = {
    'protocol': b'\x00',
    'get_ports': b'\x01',
    'enable': b'\x02',
    'disable': b'\x03',
    'reset': b'\x04'}


def _assert_protocol(protocol: str) -> None:
    if protocol != _protocol:
        raise IOError('invalid protocol header')


def _assert_version(version: tuple) -> None:
    if version[0] != _version[0] or version[1] > _version[1]:
        raise IOError(
            'version mismatch (device: {}, client: {})'.format(
                '.'.join(map(str, version)),
                '.'.join(map(str, _version))))


class Control():
    """Serial multiplexer control channel."""
    def __init__(self: object, device: str, log: BinaryIO=None) -> None:
        """
        :arg device: Device name.
        :arg log: Open writeable handle to a log file.
        """
        self._serial = serial_for_url(device)
        self._log = log

        self._ids = 0
        self._lock = 0
        self._time = time()

        sleep(2)

    def _block(self: object) -> None:
        """
        """
        while not self._serial.in_waiting:
            pass

    def _msg(self: object, device_id: str, data: bytes, way: str) -> None:
        """
        """
        if self._log:
            self._log.write('{:012.2f} {} {} {} ({})\n'.format(
                time() - self._time, way, device_id,
                ' '.join(list(map(lambda x: '{:02x}'.format(x), data))),
                len(data)))
            self._log.flush()

    def add(self: object):
        """
        """
        self._ids += 1
        return self._ids

    def read(self: object, device_id: int) -> bytes:
        """
        """
        if self._serial.in_waiting:
            if not self._lock:
                self._lock = ord(self._serial.read(1))
            if device_id == self._lock:
                self._lock = 0

                size = ord(self._serial.read(1))
                data = self._serial.read(size)
                self._msg(device_id, data, '-->')
                return data
        return b''

    def write(self: object, device_id: int, data: bytes) -> None:
        """
        """
        self._msg(device_id, data, '<--')
        self._serial.write(bytes([device_id, len(data)]) + data)


    def cmd(self: object, cmd: str) -> bytes:
        """Send a control comand.

        :arg cmd: Command.

        :returns: Resonse of control command.
        """
        self.write(0, _commands[cmd])
        self._block()
        return self.read(0)

    def init(self: object):
        """
        """
        response = self.cmd('protocol')
        _assert_protocol(response[:-3])
        _assert_version(tuple(response[-3:]))

        number_of_ports = ord(self.cmd('get_ports'))

        muxs = []
        for i in range(1, number_of_ports + 1):
            muxs.append(SerialMux(self))

        self.cmd('enable')

        return muxs
