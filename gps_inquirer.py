#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
gps_inquirer

revision 0.1  2017/may  mlabru
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Milton Abrunhosa"
__date__ = "2017/11"

# < imports >--------------------------------------------------------------------------------------

# python library
# import logging
import threading
import time

# GPSD
import gps

# < module defs >----------------------------------------------------------------------------------

# logger
# M_LOG = logging.getLogger(__name__)
# M_LOG.setLevel(logging.DEBUG)

# counters
M_CALIBRA_COUNT = 20
M_POSITION_COUNT = 300
M_WEIGHT_COUNT = 1000

# < class GPSInquirer >----------------------------------------------------------------------------

class GPSInquirer(threading.Thread):
    """
    GPSInquirer
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self, ffh_ctl):
        """
        constructor
        """
        # logger
        # M_LOG.info(">> __init__")

        # check input
        assert ffh_ctl

        # init super class
        super(GPSInquirer, self).__init__()

        # control file
        self.__fh_ctl = ffh_ctl

        # starting the stream of info
        self.__session = gps.gps(mode=gps.WATCH_ENABLE)  # |gps.WATCH_NEWSTYLE)
        assert self.__session

        # position
        self.__f_latitude = None
        self.__f_longitude = None
        self.__f_altitude = None

        self.__i_pos_count = 0

        # setting the thread running to true
        self.__v_running = True

    # ---------------------------------------------------------------------------------------------
    def init_position(self, fi_count=M_CALIBRA_COUNT):
        """
        get initial position
        """
        # logger
        # M_LOG.info(">> init_position")

        # init counter
        li_count_2d = 0
        li_count_3d = 0

        # init position
        lf_lat = lf_lng = lf_alt = 0.

        # do calibration...
        while li_count_2d < fi_count:
            # this will continue to loop and grab EACH set of gpsd info to clear the buffer
            self.__session.next()

            if not "TPV" == self.__session.data.get("class"):
                continue

            # fix 2D or 3D ?
            if self.__session.fix.mode in [2, 3]:
                # latitude
                lf_lat += self.__session.fix.latitude
                # M_LOG.debug("fix.latitude: {}".format(lf_lat))

                # longitude
                lf_lng += self.__session.fix.longitude
                # M_LOG.debug("fix.longitude: {}".format(lf_lng))

                # fix 3D ?
                if 3 == self.__session.fix.mode:
                    # altitude
                    lf_alt += self.__session.fix.altitude
                    # M_LOG.debug("fix.atitude: {}".format(lf_alt))

                    # increment counter
                    li_count_3d += 1

                # increment counter
                li_count_2d += 1
                # M_LOG.debug("li_count_2d: {}".format(li_count_2d))

        # calibration is complete ?
        if li_count_2d >= fi_count:
            # init lat/lng position
            self.__f_latitude = lf_lat / li_count_2d
            self.__f_longitude = lf_lng / li_count_2d

            # any fix 3D ?
            if li_count_3d > 0:
                # init altitude position
                self.__f_altitude = lf_alt / li_count_3d

            # senão,...
            else:
                # init altitude position
                self.__f_altitude = 0.

            # save counter
            self.__i_pos_count = li_count_2d

            # log position: time, latitude, longitude, altitude
            self.__fh_ctl.write("$POS,{:0.7f},{:0.6f},{:0.6f},{:0.2f}\n".format(time.time(), self.__f_latitude, self.__f_longitude, self.__f_altitude))
            self.__fh_ctl.flush()

            # logger
            # M_LOG.info("init_position: {}/{}({})/{}({})".format(self.__f_latitude, self.__f_longitude, li_count_2d, self.__f_altitude, li_count_3d))

    # ---------------------------------------------------------------------------------------------
    def get_position(self):
        """
        get position
        """
        # logger
        # M_LOG.info(">> get_position")

        # return
        return (self.__f_latitude, self.__f_longitude, self.__f_altitude)

    # ---------------------------------------------------------------------------------------------
    def run(self):
        """
        run
        """
        # logger
        # M_LOG.info(">> run")

        # get station number
        ls_serial = get_serial()

        # log station: time, station no
        self.__fh_ctl.write("$STN,{:0.7f},{}\n".format(time.time(), ls_serial))
        self.__fh_ctl.flush()

        # get initial position
        self.init_position(M_CALIBRA_COUNT)

        # init position
        lf_lat = self.__f_latitude
        lf_lng = self.__f_longitude
        lf_alt = self.__f_altitude

        # forever...until...
        while self.__v_running:
            #for l_report in self.__session:
            #    M_LOG.debug("report: {}".format(l_report))

            # this will continue to loop and grab EACH set of gpsd info to clear the buffer
            self.__session.next()

            # not TPV ?
            if not "TPV" == self.__session.data.get("class"):
                # next
                continue

            # fix 2D or 3D ?
            if (self.__session.fix.mode in [2, 3]) and (self.__i_pos_count >= M_CALIBRA_COUNT):
                # counter
                li_count = self.__i_pos_count

                # increment counter
                self.__i_pos_count += 1

                # latitude
                lf_lat = ((lf_lat * li_count) + self.__session.fix.latitude) / self.__i_pos_count

                # longitude
                lf_lng = ((lf_lng * li_count) + self.__session.fix.longitude) / self.__i_pos_count

                # fix 3D ?
                if 3 == self.__session.fix.mode:
                    # altitude
                    lf_alt = ((lf_alt * li_count) + self.__session.fix.altitude) / self.__i_pos_count

                # log position ?
                if 0 == (self.__i_pos_count % M_POSITION_COUNT):
                    # log position: time, latitude, longitude, altitude
                    self.__fh_ctl.write("$POS,{:0.7f},{:0.6f},{:0.6f},{:0.2f}\n".format(time.time(), lf_lat, lf_lng, lf_alt))
                    self.__fh_ctl.flush()

                    # save new position
                    self.__f_latitude = lf_lat
                    self.__f_longitude = lf_lng
                    self.__f_altitude = lf_alt

                # reset weight ?
                if 0 == (self.__i_pos_count % M_WEIGHT_COUNT):
                    # reset count
                    self.__i_pos_count = 100

    # =============================================================================================
    # data
    # =============================================================================================

    # ---------------------------------------------------------------------------------------------
    @property
    def f_altitude(self):
        return self.__f_altitude

    # ---------------------------------------------------------------------------------------------
    @property
    def f_latitude(self):
        return self.__f_latitude

    # ---------------------------------------------------------------------------------------------
    @property
    def f_longitude(self):
        return self.__f_longitude

    # ---------------------------------------------------------------------------------------------
    @property
    def v_running(self):
        return self.__v_running

    @v_running.setter
    def v_running(self, f_val):
        self.__v_running = f_val

    # ---------------------------------------------------------------------------------------------
    @property
    def session(self):
        return self.__session

# -------------------------------------------------------------------------------------------------
def get_serial():
    """
    extract serial from cpuinfo file
    """
    # logger
    # M_LOG.info(">> get_serial")

    # init string
    ls_serial = "0000000000000000"

    try:
        # open cpuinfo
        lfh_in = open("/proc/cpuinfo", 'r')

        # scan cpuinfo lines....
        for ls_line in lfh_in:
            # serial no line ?
            if "Serial" == ls_line[0:6]:
                # get serial number
                ls_serial = ls_line[10:26]

        # close file
        lfh_in.close()

    # em caso de erro...
    except:
        ls_serial = None

    # return
    return ls_serial

# < the end >--------------------------------------------------------------------------------------
