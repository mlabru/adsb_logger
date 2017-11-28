#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gps_set_clock
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import datetime
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

    try:
        # read stdin 
        for ls_data in sys.stdin:

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

    # em case de erro...
    except KeyboardInterrupt:
       pass

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:
    # logger
    # logging.basicConfig(level=logging.DEBUG)

    # exec
    main()

# <the end>----------------------------------------------------------------------------------------
