from serial import Serial
from time import sleep


connection = Serial('/dev/pts/20')

while True:
    for i in range(256):
        connection.write(bytes([i]))
        print('sent: {:02x}'.format(i))
        print('rcvd: {:02x}\n'.format(ord(connection.read())))
        sleep(1)
