#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gps_set_clock
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import datetime
#import logging
import sys
import time

# adsb
import pynmea2

# -------------------------------------------------------------------------------------------------
def __set_time(time_tuple):
    """
    set time
    """
    import ctypes
    import ctypes.util

    # /usr/include/linux/time.h:
    CLOCK_REALTIME = 0

    # /usr/include/time.h
    #
    # struct timespec
    #  {
    #    __time_t tv_sec;            /* seconds. */
    #    long int tv_nsec;           /* nanoseconds. */
    #  };
    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]

    librt = ctypes.CDLL(ctypes.util.find_library("rt"))

    ts = timespec()
    ts.tv_sec = int(time.mktime(datetime.datetime(*time_tuple[:6]).timetuple()))
    ts.tv_nsec = time_tuple[6] * 1000000 # millisecond to nanosecond

    # http://linux.die.net/man/3/clock_settime
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

# -------------------------------------------------------------------------------------------------
def main():

    print "Current date and time (before): ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # forever until...
    while True:
        try:
            # read stdin
            ls_data = sys.stdin.readline()

            if not ls_data:
                # empty line, quit
                break

        # em caso de erro...
        except KeyboardInterrupt:
            # user interrupt, quit
            break

        # invalid NMEA sentence ?
        if "$GP" != ls_data[0:3]:
            # next
            continue

        # parse NMEA sentence
        ls_msg = pynmea2.NMEASentence.parse(ls_data)

        # clock message ?
        if "$GPRMC" == ls_data[0:6]:
            # set clock time
            __set_time((ls_msg.datestamp.year,
                        ls_msg.datestamp.month,
                        ls_msg.datestamp.day,
                        ls_msg.timestamp.hour,
                        ls_msg.timestamp.minute,
                        ls_msg.timestamp.second,
                        int(ls_msg.timestamp.microsecond / 1000.)))

            # ok, quit
            break

    print "Current date and time (after): ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:
    # logger
    # logging.basicConfig(level=logging.DEBUG)

    # exec
    main()

# <the end>----------------------------------------------------------------------------------------
