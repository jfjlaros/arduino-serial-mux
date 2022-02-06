Usage
=====

The command line interface can be used to create virtual serial devices. For
more information, use the ``-h`` option.

::

    $ serial_mux -h


Initialisation
--------------

If the Arduino runs code that makes use of the serialMux protocol, like in
this sketch_, the ``serial_mux`` command will create virtual serial devices.

Start the serial multiplexer on a serial device, e.g., ``/dev/ttyUSB0``.

::

    $ serial_mux /dev/ttyUSB0
    Detected 2 virtual serial ports.
      Virtual serial device 1: /dev/pts/8
      Virtual serial device 2: /dev/pts/9


Usage
-----

We can now run the demo_ program that uses two-way communication over the
first virtual serial device.

::

    $ python demo.py /dev/pts/8
    received: 0
    received: 1
    received: 2

Simultaneously, we can look at the log messages that are written to the
second virtual serial device.

::

    $ picocom -q /dev/pts/9
    System time: 3432
    System time: 6860
    System time: 10290


.. _sketch: https://github.com/jfjlaros/serialMux/blob/master/examples/demo/demo.ino
.. _demo: https://github.com/jfjlaros/arduino-serial-mux/blob/master/examples/demo/demo.py
