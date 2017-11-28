#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
adsb_logger

revision 0.1  2017/nov  mlabru
initial release (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.1$"
__author__ = "Milton Abrunhosa"
__date__ = "2017/11"

# < imports >--------------------------------------------------------------------------------------

# python library
import datetime
import logging
import os
import sys
import time

# adsb_logger
import adsb_inquirer as adi
import gps_inquirer as gpi

# -------------------------------------------------------------------------------------------------
def main():
    """
    drive app
    """
    # hostname
    ls_host = os.uname()[1]

    # data
    ls_date = datetime.datetime.now().strftime("%Y%m%d.%H%M")
        
    # goto exec dir
    os.chdir(os.path.dirname(sys.argv[0]))

    # create out file: adsb_logger.<host>.<data>.<hora>.dat
    lfh_dat = open("logs/adsb_logger.{}.{}.dat".format(ls_host, ls_date), "w")
    assert lfh_dat

    # create control file: adsb_logger.<host>.<data>.<hora>.ctl
    lfh_ctl = open("logs/adsb_logger.{}.{}.ctl".format(ls_host, ls_date), "w")
    assert lfh_ctl

    # create the thread gps inquirer
    l_gpsi = gpi.GPSInquirer(lfh_ctl)
    assert l_gpsi

    # create the thread adsb inquirer
    l_adsi = adi.ADSBInquirer(l_gpsi, lfh_dat)
    assert l_adsi

    try:
        # start it up
        l_gpsi.start()

        # start it up
        l_adsi.start()

        while l_gpsi.v_running:
            time.sleep(1)

    # em caso de erro...
    except (KeyboardInterrupt, SystemExit):
        # when you press ctrl+c
        print "killing threads..."

        # stop running
        l_gpsi.v_running = False
        # wait for the threads to finish what it's doing
        l_gpsi.join()
        l_adsi.join()

    # close output file
    lfh_dat.close()

    # close control file
    lfh_ctl.close()

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:
    # logger
    logging.basicConfig(level=logging.DEBUG)

    # exec
    main()

    # end app
    sys.exit()
    
# <the end>----------------------------------------------------------------------------------------
