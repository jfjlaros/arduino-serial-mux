from os import fork
from serial import serial_for_url
from time import sleep, time
from typing import BinaryIO

from .vserial import VSerial


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


class SerialMux():
    """Serial multiplexer."""
    def __init__(self: object, device: str, log: BinaryIO=None) -> None:
        """
        :arg device: Device name.
        :arg log: Open writeable handle to a log file.
        """
        self._serial = serial_for_url(device)
        self._log = log

        self._time = time()
        self._device = []

        sleep(2)

        number_of_ports = ord(self._cmd('get_ports'))

        for i in range(1, number_of_ports + 1):
            self._device.append(VSerial(self, i))

        self._cmd('enable')

        pid = fork()
        if pid:
            while True:
                self._update();

    def write(self: object, device_id: int, data: bytes) -> None:
        """
        """
        self._write(device_id, data)
        self._msg(device_id, data, '<--')

    def get_ports(self: object) -> list:
        """
        """
        return [device.name for device in self._device]

    def _update(self: object) -> None:
        """
        """
        device_id, data = self._read()
        self._device[device_id - 1].receive(data)
        self._msg(device_id, data, '-->')

    def _cmd(self: object, cmd: str) -> bytes:
        """Send a control comand.

        :arg cmd: Command.

        :returns: Resonse of control command.
        """
        self.write(0, _commands[cmd])
        device_id, data = self._read()
        if device_id or not data:
            raise IOError('invalid control command response')
        return data

    def _msg(self: object, device_id: str, data: bytes, way: str) -> None:
        """
        """
        if self._log:
            self._log.write('{:012.2f} {} {} {} ({})\n'.format(
                time() - self._time, way, device_id,
                ' '.join(list(map(lambda x: '{:02x}'.format(x), data))),
                len(data)))
            self._log.flush()

    def _read(self: object) -> tuple:
        """
        """
        device_id = ord(self._serial.read())
        size = ord(self._serial.read())
        data = self._serial.read(size)
        return device_id, data

    def _write(self: object, device_id: int, data: bytes) -> None:
        """
        """
        self._serial.write(bytes([device_id, len(data)]) + data)
