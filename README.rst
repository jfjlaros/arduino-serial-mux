Arduino serialMux host library
==============================

.. NOTE::

    Under construction.

----

Installation
------------

::

    git clone https://github.com/jfjlaros/arduino-simple-rpc
    cd arduino-simple-rpc
    pip install .


Usage
-----

Start the serial multiplexer on a serial device, e.g., ``/dev/ttyUSB0``.

::

    $ serial_mux /dev/ttyUSB0
    Virtual ports detected: 2
      Mux1: /dev/pts/8
      Mux2: /dev/pts/9

Run the demo_ (needs simpleRPC_).

::

    $ python demo.py /dev/pts/8

In an other terminal, see the log messages.

::

    $ picocom /dev/pts/9


.. _demo: https://github.com/jfjlaros/arduino-serial-mux/blob/master/examples/demo/demo.py
.. _simpleRPC: https://pypi.org/project/arduino-simple-rpc/
