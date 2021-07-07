#!/usr/bin/env python
import argparse
import array
import logging
import time
import sys

import usb.core
import usb.util


CONTROL_CBC = 5
REQ_TYPE_GET_INTERFACE = 0xa1
REQ_TYPE_SET_INTERFACE = 0x21
HID_GET_REPORT = 0x01
HID_SET_REPORT = 0x09
INIT = 0x0303
MOVE = 0x0305
GET_STATUS = 0x0304
BUF_LEN = 64
MODE_OF_OPERATION = 0x03
MODE_OF_OPERATION_DEFAULT = 0x04


class Logger:
    """
    Simple logger class with output on console only
    """
    def __init__(self, logger_name):
        """
        Initialize named logger
        """
        self._log = logging.getLogger(logger_name)
        self.setup_logger()
        self._log.set_verbose = self.set_verbose

    def __call__(self):
        """
        Calling this object will return configured logging.Logger object with
        additional set_verbose() method.
        """
        return self._log

    def set_verbose(self, verbose_level, quiet_level):
        """
        Change verbosity level. Default level is warning.
        """
        self._log.setLevel(logging.WARNING)

        if quiet_level:
            self._log.setLevel(logging.ERROR)
            if quiet_level > 1:
                self._log.setLevel(logging.CRITICAL)

        if verbose_level:
            self._log.setLevel(logging.INFO)
            if verbose_level > 1:
                self._log.setLevel(logging.DEBUG)

    def setup_logger(self):
        """
        Create setup instance and make output meaningful :)
        """
        if self._log.handlers:
            # need only one handler
            return

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.set_name("console")
        console_formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_formatter)
        self._log.addHandler(console_handler)
        self._log.setLevel(logging.WARNING)


LOG = Logger(__name__)()


class StatusReport:
    """
    Get the status: position and movement

    Measurement height in cm has been taken manually. In minimal height,
    height from floor to the underside of the desktop and is 67cm. Note, this
    value may differ, since mine desk have wheels. In maximal elevation, it is
    132cm.
    For readings from the USB device, numbers are absolute, and have values of
    0 and 6480 for min and max positions.

    Exposed position information in cm is than taken as a result of the
    equation:

        position_in_cm = actual_read_position / (132 - 67) + 67

    """

    def __init__(self, raw_response):
        self.moving = raw_response[6] > 0
        self.position = raw_response[4] + (raw_response[5] << 8)
        self.position_in_cm = self.position / 65 + 67


class LinakDevice:
    """
    Class representing USB interface for Linak controller USB2LIN06
    """

    VEND = 0x12d3
    PROD = 0x0002

    def __init__(self):
        self._dev = usb.core.find(idVendor=LinakDevice.VEND,
                                  idProduct=LinakDevice.PROD)

        # detach kernel driver, if attached
        if self._dev.is_kernel_driver_active(0):
            self._dev.detach_kernel_driver(0)

        # init device
        buf = [0 for _ in range(BUF_LEN)]
        buf[0] = MODE_OF_OPERATION          # 0x03 Feature report ID = 3
        buf[1] = MODE_OF_OPERATION_DEFAULT  # 0x04 mode of operation
        buf[2] = 0x00                       # ?
        buf[3] = 0xfb                       # ?
        self._dev.ctrl_transfer(REQ_TYPE_SET_INTERFACE, HID_SET_REPORT, INIT,
                                0, array.array('B', buf))
        # hold a little bit, to make it effect.
        time.sleep(0.5)

    def get_position(self, args):
        try:
            while True:
                report = self._get_report()
                LOG.warning('Position: %s, height: %.2fcm, moving: %s',
                            report.position, report.position_in_cm,
                            report.moving)
                if not args.loop:
                    break
                time.sleep(0.2)
        except KeyboardInterrupt:
            return

    def move(self, args):
        retry_count = 3
        previous_position = 0

        while True:
            self._move(args.position)
            time.sleep(0.2)

            status_report = self._get_report()
            LOG.info("Current position: %s", status_report.position)

            if status_report.position == args.position:
                break

            if previous_position == status_report.position:
                LOG.debug("Position is same as previous one: %s",
                          previous_position)
                retry_count -= 1

            previous_position = status_report.position

            if retry_count == 0:
                LOG.debug("Retry has reached its threshold. Stop moving.")
                break

    def _get_report(self):
        raw = self._dev.ctrl_transfer(REQ_TYPE_GET_INTERFACE, HID_GET_REPORT,
                                      GET_STATUS, 0, BUF_LEN)
        LOG.debug(raw)
        return StatusReport(raw)

    def _move(self, position):
        buf = [0 for _ in range(BUF_LEN)]
        pos = "%04x" % position  # for example: 0x02ff
        pos_l = int(pos[2:], 16)  # 0xff
        pos_h = int(pos[:2], 16)  # 0x02

        buf[0] = CONTROL_CBC
        # For my desk controller, seting position bytes on indexes 1 and 2 are
        # effective, the other does nothing in my case, although there might
        # be some differences on other hw.
        buf[1] = buf[3] = buf[5] = buf[7] = pos_l
        buf[2] = buf[4] = buf[6] = buf[8] = pos_h
        self._dev.ctrl_transfer(REQ_TYPE_SET_INTERFACE, HID_SET_REPORT, MOVE,
                                0, array.array('B', buf))


def main():
    device = LinakDevice()

    parser = argparse.ArgumentParser('An utility to interact with USB2LIN06 '
                                     'device.')
    subparsers = parser.add_subparsers(help='supported commands',
                                       dest='subcommand')
    subparsers.required = True
    parser_status = subparsers.add_parser('status', help='get status of the '
                                          'device.')
    parser_status.add_argument('-l', '--loop', help='run indefinitely, use '
                               'ctrl-c to stop.', action="store_true")
    parser_status.set_defaults(func=device.get_position)
    parser_move = subparsers.add_parser('move', help='move to the desired '
                                        'height. Note, that height need to be '
                                        'provided as reported by status.')
    parser_move.add_argument('position', type=int)
    parser_move.set_defaults(func=device.move)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", help='please, be quiet. Adding more '
                       '"q" will decrease verbosity', action="count",
                       default=0)
    group.add_argument("-v", "--verbose", help='be verbose. Adding more "v" '
                       'will increase verbosity', action="count", default=0)
    args = parser.parse_args()

    LOG.set_verbose(args.verbose, args.quiet)

    args.func(args)


if __name__ == '__main__':
    main()
