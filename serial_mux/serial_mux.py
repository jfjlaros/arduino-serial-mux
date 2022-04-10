from serial import serial_for_url
from threading import Lock
from time import sleep, time
from typing import BinaryIO

from .vserial import VSerial


_protocol = b'serialMux'
_version = (2, 0, 0)
_escape = b'\xff'
_control_port = 0xfe
_commands = {
    'protocol': b'\x00',
    'version': b'\x01',
    'get_ports': b'\x02',
    'enable': b'\x03',
    'disable': b'\x04',
    'reset': b'\x05'}


class SerialMux():
    """Serial multiplexer."""
    def __init__(
            self: object, device: str, baudrate: int=9600, wait: int=2,
            log: BinaryIO=None) -> None:
        """
        :arg device: Device name.
        :arg baudrate: Baud rate.
        :arg wait: Time in seconds before communication starts.
        :arg log: Open writeable handle to a log file.
        """
        self._log = log
        self._mutex = Lock()

        self._port_rx = _control_port
        self._port_tx = _control_port

        self._serial = serial_for_url(device, baudrate=baudrate)
        sleep(wait)

        _assert_protocol(self._cmd('protocol', len(_protocol)))
        _assert_version(self._cmd('version', len(_version)))
        number_of_ports = ord(self._cmd('get_ports', 1))

        self.devices = []
        for i in range(number_of_ports):
            self.devices.append(VSerial(self, i))

        self._cmd('enable', 1)

    def send(self: object, port: int, data: bytes) -> None:
        """Send data from a virtual serial device to the serial device.

        :arg port: Virtual serial port.
        :arg data: Data.
        """
        with self._mutex:
            self._write(port, data)

    def update(self: object) -> None:
        """Receive serial data and send it to the corresponding virtual
        serial device."""
        while True:
            self._update()

    def _cmd(self: object, cmd: str, size: int) -> bytes:
        """Send a control comand.

        :arg cmd: Command.

        :returns: Resonse of control command.
        """
        self._write(_control_port, _commands[cmd])
        data = self.read(size)
        if self._port_rx != _control_port or not data:
            raise IOError('invalid control command response')
        return data

    def _update(self: object) -> None:
        """Receive serial data and send it to the corresponding virtual
        serial device."""
        data = self.read(1)
        if self._port_rx != _control_port:
            self.devices[self._port_rx].receive(data)

    def read(self: object, size: int) -> bytes:
        """Read from the serial device.

        :size: Number of bytes to read.

        :returns: Virtual serial port and data.
        """
        data = b''.join([self._read() for _ in range(size)])
        self._msg(self._port_rx, data, '-->')
        return data

    def _msg(self: object, port: str, data: bytes, way: str) -> None:
        """Log a message.

        :arg port: Virtual serial port.
        :arg data: Data.
        :arg way: Data transfer direction.
        """
        if self._log:
            self._log.write('{:012.2f} {} {:02x} : {} ({})\n'.format(
                time(), way, port, _hex(data), len(data)))
            self._log.flush()

    def _read(self: object) -> bytes:
        """Read from the serial device.

        :returns: Data.
        """
        while (byte := self._serial.read()) == _escape:
            port = self._serial.read()
            if port == _escape:
                return _escape
            else:
                self._port_rx = ord(port)
        return byte

    def _write(self: object, port: int, data: bytes) -> None:
        """Write to the serial device.

        :arg port: Virtual serial port.
        :arg data: Data.
        """
        if port != self._port_tx:
            self._port_tx = port
            self._serial.write(_escape + bytes([self._port_tx]))
        for byte in [bytes([b]) for b in data]:
            if byte == _escape:
                self._serial.write(_escape)
            self._serial.write(byte)
        self._msg(self._port_tx, data, '<--')


def _assert_protocol(protocol: str) -> None:
    if protocol != _protocol:
        raise IOError('invalid protocol header')


def _assert_version(version: tuple) -> None:
    if version[0] != _version[0] or version[1] > _version[1]:
        raise IOError(
            'version mismatch (device: {}, client: {})'.format(
                '.'.join(map(str, version)),
                '.'.join(map(str, _version))))


def _hex(data: bytes) -> str:
    return ' '.join(list(map(lambda x: '{:02x}'.format(x), data)))
