#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
adsb_inquirer

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
import sys
import threading
import time

# < module defs >----------------------------------------------------------------------------------

# logger
# M_LOG = logging.getLogger(__name__)
# M_LOG.setLevel(logging.DEBUG)

# < class ADSBInquirer >---------------------------------------------------------------------------

class ADSBInquirer(threading.Thread):
    """
    ADSBInquirer
    """
    # ---------------------------------------------------------------------------------------------
    def __init__(self, f_gpsi, ffh_dat):
        """
        constructor
        """
        # logger
        # M_LOG.info(">> __init__")

        # check input
        assert f_gpsi
        assert ffh_dat

        # init super class
        super(ADSBInquirer, self).__init__()

        # gpsd
        self.__gps = f_gpsi

        # data file
        self.__fh_dat = ffh_dat

        # init squitter counters
        self.__i_error = 0
        self.__i_short = 0
        self.__i_extended = 0

        # setting the thread running to true
        self.__v_running = True

    # ---------------------------------------------------------------------------------------------
    def run(self):
        """
        run
        """
        # logger
        # M_LOG.info(">> run")

        try:
            # forever...
            while self.__gps.v_running:
                # adsb message
                ls_line = sys.stdin.readline()

                # time of arrival
                li_now = time.time()

                # build message toa, lst_pos, message
                self.__fh_dat.write("{:0.7f}#{}#{}".format(li_now, self.__gps.get_position(), ls_line))

                # extended squitter ?
                if len(ls_line) >= 30:
                    # increment extended counter
                    self.__i_extended += 1

                # short squitter ?
                elif len(ls_line) >= 16:
                    # increment short counter
                    self.__i_short += 1

                # senão,...
                else:
                    # increment error counter
                    self.__i_error += 1

        # em caso de erro...
        except (KeyboardInterrupt, SystemExit):
            # flush stdout
            sys.stdout.flush()

            # stop thread
            self.__v_running = False

    # =============================================================================================
    # data
    # =============================================================================================

    # ---------------------------------------------------------------------------------------------
    @property
    def i_error(self):
        return self.__i_error

    # ---------------------------------------------------------------------------------------------
    @property
    def i_extended(self):
        return self.__i_extended

    # ---------------------------------------------------------------------------------------------
    @property
    def i_short(self):
        return self.__i_short

    # ---------------------------------------------------------------------------------------------
    @property
    def v_running(self):
        return self.__v_running

    @v_running.setter
    def v_running(self, f_val):
        self.__v_running = f_val

# < the end >--------------------------------------------------------------------------------------
