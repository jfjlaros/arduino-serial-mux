from time import sleep

from simple_rpc import Interface


interface = Interface('/dev/pts/14', wait=2)

while True:
    for i in range(256):
        print(interface.inc(i))
        sleep(1);
