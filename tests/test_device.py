from os.path import exists
from pytest import mark
from serial import Serial
from time import sleep

from serial_mux import SerialMux
from sys import stderr


_device = '/dev/ttyUSB0'


@mark.skipif(not exists(_device), reason='device not connected')
class TestDevice(object):
    if exists(_device):
        _mux = SerialMux(_device)

    def test_ports(self: object) -> None:
        assert len(self._mux.devices) == 2

    def test_device1(self: object) -> None:
        serial = Serial(self._mux.devices[0].name)
        serial.write(b'\x01')
        self._mux.devices[0]._update()
        for _ in range(64):
            self._mux._update()

        assert serial.read(11) == b'received: 1'

    def test_device2(self: object) -> None:
        in_handle = open(self._mux.devices[1].name, 'rb')
        self._mux._update()
        assert in_handle.read(6) == b'time: '
