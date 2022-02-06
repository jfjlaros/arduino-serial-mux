from pkg_resources import DistributionNotFound, get_distribution

from .serial_mux import SerialMux
from .vserial import VSerial


def _get_metadata(name: str) -> str:
    try:
        pkg = get_distribution('arduino_serial_mux')
    except DistributionNotFound:
        pkg = get_distribution('serial_mux')

    for line in pkg.get_metadata_lines(pkg.PKG_INFO):
        if line.startswith('{}: '.format(name)):
            return line.split(': ')[1]

    return ''


_copyright_notice = 'Copyright (c) {} <{}>'.format(
    _get_metadata('Author'), _get_metadata('Author-email'))

usage = [_get_metadata('Summary'), _copyright_notice]


def doc_split(func: callable) -> str:
    return func.__doc__.split('\n\n')[0]


def version(name: str) -> str:
    return '{} version {}\n\n{}\nHomepage: {}'.format(
        _get_metadata('Name'), _get_metadata('Version'), _copyright_notice,
        _get_metadata('Home-page'))
