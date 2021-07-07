==========
Linak-ctrl
==========

.. image:: https://badge.fury.io/py/linak-ctrl.svg
   :target: https://badge.fury.io/py/linak-ctrl

Simple python script to control Linak powered desks and USB2LIN06 cable.


Requirements
============

* Linak desk ;)
* USB2LIN06 device
* Python
* `pyusb`_


Installation
============

There are couple of different ways for installing ``linak-ctrl``. One of the
preferred ways is to use virtualenv and pip:

.. code:: shell-session

   $ git clone https://github.com/gryf/linak-ctrl
   $ cd linak-ctrl
   linak-ctrl $ python -m venv linak
   (linak) linak-ctrl $ pip install .
   (linak) linak-ctrl $ linak-ctrl status
   Position: 767, height: 78.80cm, moving: False

Or, you can install it system-wide:

.. code:: shell-session

   $ sudo pip install linak-ctrl

And finally, you could also install dependences from your system repositories,
and use script directly, by placing it somewhere in your ``$PATH``.


Usage
=====

Currently, script have two available commands: ``status`` and ``move``.

Invoking ``status`` will give information about desk height - both in absolute
number, and in centimeters, and information if desk is moving.

.. code:: shell-session

   $ linak_ctrl.py status
   Position: 767, height: 78.80cm, moving: False

Note, that height was measured manually and may differ depending if desk have
casters or regular foots.

Command ``status`` accept optional parameter ``--loop`` for fetching
information from USB2LIN06 device every 0.2 seconds:

.. code:: shell-session

   $ linak_ctrl.py status -l
   Position: 2161, height: 100.25cm, moving: True
   Position: 2109, height: 99.45cm, moving: True
   Position: 2026, height: 98.17cm, moving: True
   Position: 1960, height: 97.15cm, moving: True
   Position: 1872, height: 95.80cm, moving: True
   Position: 1797, height: 94.65cm, moving: True
   Position: 1728, height: 93.58cm, moving: True
   Position: 1675, height: 92.77cm, moving: True
   Position: 1652, height: 92.42cm, moving: True
   Position: 1651, height: 92.40cm, moving: False

Command ``move`` is used for adjusting desk height. It needs parameter
``position``, which is absolute number, and its range is between 0 and 6480 (in
my case). For example:

.. code:: shell-session

   $ linak_ctrl.py move 1000

For displaying debug information verbosity can be increased using ``--verbose``
parameter:

.. code:: shell-session

   $ linak_ctrl.py -v move 1000
   Current position: 771
   Current position: 792
   Current position: 825
   Current position: 873
   Current position: 939
   Current position: 988
   Current position: 1000

Adding more `-v` will increase amount of information:

.. code:: shell-session

   $ linak_ctrl.py -vv move 1000
   array('B', [4, 56, 17, 8, 3, 3, 0, 57, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0])
   Current position: 771
   array('B', [4, 56, 17, 0, 21, 3, 0, 129, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0])
   Current position: 789
   array('B', [4, 56, 17, 0, 55, 3, 0, 205, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0])
   Current position: 823
   array('B', [4, 56, 17, 0, 101, 3, 16, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0])
   Current position: 869
   array('B', [4, 56, 17, 0, 162, 3, 16, 92, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0])
   Current position: 930
   array('B', [4, 56, 17, 0, 217, 3, 0, 170, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0])
   Current position: 985
   array('B', [4, 56, 17, 0, 232, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 232, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0])
   Current position: 1000


Alternatives
============

There are two projects, which more or less are doing the same. Fist one can be
treated as a reference project - lots of information in the source code, second
one is a python project, which uses `libusb1`_ wrapper library instead of
`pyusb`_:

* `usb2lin06-HID-in-linux-for-LINAK-Desk-Control-Cable`_
* `python-linak-desk-control`_


License
=======

This software is licensed under 3-clause BSD license. See LICENSE file for
details.


.. _pyusb: https://github.com/pyusb/pyusb
.. _usb2lin06-HID-in-linux-for-LINAK-Desk-Control-Cable: https://github.com/UrbanskiDawid/usb2lin06-HID-in-linux-for-LINAK-Desk-Control-Cable
.. _python-linak-desk-control: https://github.com/monofox/python-linak-desk-control
.. _libusb1: https://github.com/vpelletier/python-libusb1
