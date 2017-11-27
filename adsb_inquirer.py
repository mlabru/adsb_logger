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

# from timeit import default_timer as timer

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

        # setting the thread running to true
        # self.__v_running = True
   
    # ---------------------------------------------------------------------------------------------
    def run(self):
        """
        run
        """        
        # logger
        # M_LOG.info(">> run")
        
        # init message counter
        # li_msg_count = 0

        try:
            # forever...
            while self.__gps.v_running:
                # build message toa, message, lst_pos
                self.__fh_dat.write("{:0.7f}#{}#{}".format(time.time(), self.__gps.get_position(), sys.stdin.readline()))

                # increment message counter
                # li_msg_count += 1

        # em caso de erro...
        except (KeyboardInterrupt, SystemExit):
            # flush stdout  
            sys.stdout.flush()

        # logger
        # print "<<< total de mensagens: {}".format(li_msg_count)

    # =============================================================================================
    # data
    # =============================================================================================
    '''            
    # ---------------------------------------------------------------------------------------------
    @property
    def v_running(self):
        return self.__v_running

    @v_running.setter
    def v_running(self, f_val):
        self.__v_running = f_val
    '''
# < the end >--------------------------------------------------------------------------------------
