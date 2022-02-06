from serial_mux import SerialMux
from serial_mux.serial_mux import (
    _assert_protocol, _assert_version, _commands, _protocol,
    _version)


def test_assert_protocol_pass() -> None:
    _assert_protocol(_protocol)


def test_assert_protocol_fail() -> None:
    try:
        _assert_protocol('')
    except IOError as error:
        assert str(error) == 'invalid protocol header'
    else:
        assert False


def test_assert_version_pass() -> None:
    _assert_version(_version)


def test_assert_version_fail() -> None:
    try:
        _assert_version((0, 0, 0))
    except IOError as error:
        assert str(error).startswith('version mismatch')
    else:
        assert False


def test_init() -> None:
    assert SerialMux('', wait=0)


def test_cmd() -> None:
    mux = SerialMux('', wait=0)
    for k, v in _commands.items():
        mux._serial.prepare(b'\xff\x01\x00')
        assert mux._cmd(k) == b'\x00'
        assert mux._serial.inspect(3) == b'\xff\x01' + v


def test_cmd_fail_1() -> None:
    mux = SerialMux('', wait=0)
    mux._serial.prepare(b'\x00\x01\x00')
    try:
        mux._cmd('protocol')
    except IOError as error:
        assert str(error) == 'invalid control command response'
    else:
        assert False


def test_cmd_fail_2() -> None:
    mux = SerialMux('', wait=0)
    mux._serial.prepare(b'\xff\x00\x00')
    try:
        mux._cmd('protocol')
    except IOError as error:
        assert str(error) == 'invalid control command response'
    else:
        assert False


def test_read() -> None:
    mux = SerialMux('', wait=0)
    mux._serial.prepare(b'\x00\x01\xff')
    assert mux._read() == (0, b'\xff')


def test_write() -> None:
    mux = SerialMux('', wait=0)
    mux._write(0, b'\xff')
    assert mux._serial.inspect(3) == b'\x00\x01\xff'


def test_send() -> None:
    mux = SerialMux('', wait=0)
    mux.send(0, b'\xff')
    assert mux._serial.inspect(3) == b'\x00\x01\xff'


def test_devices() -> None:
    mux = SerialMux('', wait=0)
    assert len(mux.devices) == 2


def test_send_device1() -> None:
    mux = SerialMux('', wait=0)
    handle = open(mux.devices[0].name, 'wb')
    handle.write(b'\x01\x02\x03')
    handle.flush()
    mux.devices[0]._update()
    assert mux._serial.inspect(5) == b'\x00\x03\x01\x02\x03'


def test_send_device2() -> None:
    mux = SerialMux('', wait=0)
    handle = open(mux.devices[1].name, 'wb')
    handle.write(b'\x01\x02\x03')
    handle.flush()
    mux.devices[1]._update()
    assert mux._serial.inspect(5) == b'\x01\x03\x01\x02\x03'


def test_receive_direct_device1() -> None:
    mux = SerialMux('', wait=0)
    handle = open(mux.devices[0].name, 'rb')
    mux.devices[0].receive(b'\xff')
    assert handle.read(1) == b'\xff'


def test_receive_device1() -> None:
    mux = SerialMux('', wait=0)
    handle = open(mux.devices[0].name, 'rb')
    mux._serial.prepare(b'\x00\x01\xff')
    mux._update()
    assert handle.read(1) == b'\xff'


def test_receive_direct_device2() -> None:
    mux = SerialMux('', wait=0)
    handle = open(mux.devices[1].name, 'rb')
    mux.devices[1].receive(b'\xff')
    assert handle.read(1) == b'\xff'


def test_receive_device2() -> None:
    mux = SerialMux('', wait=0)
    handle = open(mux.devices[1].name, 'rb')
    mux._serial.prepare(b'\x01\x01\xff')
    mux._update()
    assert handle.read(1) == b'\xff'
