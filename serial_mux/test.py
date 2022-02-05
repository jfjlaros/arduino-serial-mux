from os import fork

from .serial_mux import SerialMux


mux = SerialMux('/dev/ttyUSB0', open('log.txt', 'w'))


ports = mux.get_ports()
print('Detected {} ports.'.format(len(ports)))
for index, port in enumerate(ports):
    print('  Virtual serial device {}: {}'.format(index + 1, port))
