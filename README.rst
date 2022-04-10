Arduino serialMux host library
==============================

.. image:: https://img.shields.io/github/last-commit/jfjlaros/arduino-serial-mux.svg
   :target: https://github.com/jfjlaros/arduino-serial-mux/graphs/commit-activity
.. image:: https://github.com/jfjlaros/arduino-serial-mux/actions/workflows/python-package.yml/badge.svg
   :target: https://github.com/jfjlaros/arduino-serial-mux/actions/workflows/python-package.yml
.. image:: https://readthedocs.org/projects/serialmux/badge/?version=latest
   :target: https://arduino-serial-mux.readthedocs.io/en/latest
.. image:: https://img.shields.io/github/release-date/jfjlaros/arduino-serial-mux.svg
   :target: https://github.com/jfjlaros/arduino-serial-mux/releases
.. image:: https://img.shields.io/github/release/jfjlaros/arduino-serial-mux.svg
   :target: https://github.com/jfjlaros/arduino-serial-mux/releases
.. image:: https://img.shields.io/pypi/v/arduino-serial-mux.svg
   :target: https://pypi.org/project/arduino-serial-mux/
.. image:: https://img.shields.io/github/languages/code-size/jfjlaros/arduino-serial-mux.svg
   :target: https://github.com/jfjlaros/arduino-serial-mux
.. image:: https://img.shields.io/github/languages/count/jfjlaros/arduino-serial-mux.svg
   :target: https://github.com/jfjlaros/arduino-serial-mux
.. image:: https://img.shields.io/github/languages/top/jfjlaros/arduino-serial-mux.svg
   :target: https://github.com/jfjlaros/arduino-serial-mux
.. image:: https://img.shields.io/github/license/jfjlaros/arduino-serial-mux.svg
   :target: https://raw.githubusercontent.com/jfjlaros/arduino-serial-mux/master/LICENSE.md

----

This Python library provides a simple way to create virtual serial interfaces
created on an Arduino_ using the serialMux_ protocol.

Please see ReadTheDocs_ for the latest documentation.

Quick start
-----------

Plug in the Arduino device and run the serial multiplexer.

::

    $ serial_mux /dev/ttyUSB0
    Detected 2 virtual serial ports.
      Virtual serial device 1: /dev/pts/8
      Virtual serial device 2: /dev/pts/9

The virtual serial devices ``/dev/pts/8`` and ``/dev/pts/9`` can now be used to
communicate to the virtual serial devices created on the device.

For more information, see the Usage_ section.


.. _Arduino: https://www.arduino.cc
.. _serialMux: https://serialmux.readthedocs.io
.. _ReadTheDocs: https://arduino-serial-mux.readthedocs.io
.. _Usage: https://arduino-serial-mux.readthedocs.io/en/latest/usage.html
