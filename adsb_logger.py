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
import threading
import time

# i2c lcd
import I2C_LCD_driver

# adsb_logger
import adsb_inquirer as adi
import gps_inquirer as gpi

# < module defs >----------------------------------------------------------------------------------

# logger
# M_LOG = logging.getLogger(__name__)
# M_LOG.setLevel(logging.DEBUG)

# lines for gps inquirer
M_LIN_GPS_1 = 1
M_LIN_GPS_2 = 2

# lines for adsb inquirer
M_LIN_ADS_1 = 3
M_LIN_ADS_2 = 4

# -------------------------------------------------------------------------------------------------
def update_display(f_lcd, fthr_gpsi, fthr_adsi):
    """
    update display
    """
    # logger
    # M_LOG.info(">> update_display")

    # check input
    assert f_lcd 
    assert fthr_gpsi 
    assert fthr_adsi

    # forever...until
    while fthr_gpsi.v_running:

        # latitude
        lf_lat = fthr_gpsi.f_latitude
        ls_lat = "{:0.2f}".format(lf_lat) if lf_lat is not None else "None"

        # longitude
        lf_lng = fthr_gpsi.f_longitude
        ls_lng = "{:0.2f}".format(lf_lng) if lf_lng is not None else "None"

        # altitude
        # lf_alt = fthr_gpsi.f_altitude
        # ls_alt = "{:0.1f}".format(lf_alt) if lf_alt is not None else "None"

        # show display
        f_lcd.lcd_display_string("DT:{}".format(time.strftime("%d/%m/%y %H:%M:%S")), M_LIN_GPS_1, 0)
        f_lcd.lcd_display_string("F:{} P:{}/{}".format(fthr_gpsi.session.fix.mode, ls_lat, ls_lng), M_LIN_GPS_2, 0)

        # sleep 1s
        time.sleep(1)

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
    lthr_gpsi = gpi.GPSInquirer(lfh_ctl)
    assert lthr_gpsi

    # create the thread adsb inquirer
    lthr_adsi = adi.ADSBInquirer(lthr_gpsi, lfh_dat)
    assert lthr_adsi

    # create lcd driver
    l_lcd = I2C_LCD_driver.lcd()
    assert l_lcd

    # clear screen
    l_lcd.lcd_clear()

    # create thread update display
    lthr_upd_dsp = threading.Thread(target=update_display, args=(l_lcd, lthr_gpsi, lthr_adsi))
    assert lthr_upd_dsp 

    try:
        # start it up
        lthr_gpsi.start()

        # start it up
        lthr_adsi.start()

        # start update display
        lthr_upd_dsp.start()

        # forever...until
        while lthr_gpsi.v_running:
            # sleep 1s
            time.sleep(1)

    # em caso de erro...
    except (KeyboardInterrupt, SystemExit):
        # when you press ctrl+c
        print "killing threads..."

        # stop running
        lthr_gpsi.v_running = False
        # wait for the threads to finish what it's doing
        lthr_gpsi.join()
        lthr_adsi.join()
        lthr_upd_dsp.join()

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
