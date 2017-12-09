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
import optparse
import os
import subprocess
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

# display lines
M_LIN_SYS = 1
M_LIN_DAT = 2
M_LIN_GPS = 3
M_LIN_ADS = 4

# -------------------------------------------------------------------------------------------------
def get_wifi():
    """
    get_wifi
    """
    # logger
    # M_LOG.info(">> get_wifi")

    # init SSID
    ls_ssid = ">no wifi<"

    # get iwconfig output
    ls_scan_output = subprocess.check_output(["iwconfig", "wlan0"])
    # M_LOG.debug("ls_scan_output: {}".format(ls_scan_output))

    # for all output tokens...
    for ls_tok in ls_scan_output.split():
        # ESSID token ?
        if ls_tok.startswith("ESSID:"):
            # get SSID
            return ls_tok.split('"')[1]

    # return
    return ls_ssid

# -------------------------------------------------------------------------------------------------
def update_display(fthr_gpsi, fthr_adsi, fv_display=True):
    """
    update display
    """
    # logger
    # M_LOG.info(">> update_display")

    # check input
    assert fthr_gpsi
    assert fthr_adsi

    # no display ?
    if not fv_display:
        # return
        return

    # create lcd driver
    l_lcd = I2C_LCD_driver.lcd()
    assert l_lcd

    # clear screen
    l_lcd.lcd_clear()

    # forever...until
    while fthr_adsi.v_running and fthr_gpsi.v_running:

        # 12345678901234567890
        #  icbox-21 sophosAir

        # show system line
        f_lcd.lcd_display_string(" {} {}".format(os.uname()[1], get_wifi()), M_LIN_SYS, 0)

        # 12345678901234567890
        #  99/99/99  99:99:99

        # show date line
        f_lcd.lcd_display_string(" {}".format(time.strftime("%d/%m/%y  %H:%M:%S")), M_LIN_DAT, 0)

        # latitude
        lf_lat = fthr_gpsi.f_latitude
        ls_lat = "{:0.2f}".format(lf_lat) if lf_lat is not None else "None"

        # longitude
        lf_lng = fthr_gpsi.f_longitude
        ls_lng = "{:0.2f}".format(lf_lng) if lf_lng is not None else "None"

        # altitude
        # lf_alt = fthr_gpsi.f_altitude
        # ls_alt = "{:0.1f}".format(lf_alt) if lf_alt is not None else "None"

        # 12345678901234567890
        # F:0 P:-12.34/-012.34

        # show gps line
        f_lcd.lcd_display_string("F:{} P:{}/{}".format(fthr_gpsi.session.fix.mode, ls_lat, ls_lng), M_LIN_GPS, 0)

        # ajusta para display
        li_short = fthr_adsi.i_short % 10000
        li_extended = fthr_adsi.i_extended % 10000
        li_error = fthr_adsi.i_error % 10000

        # 12345678901234567890
        # S:0000 X:0000 S:99/9

        # show adsb line
        f_lcd.lcd_display_string("S:{:4d} X:{:4d} S:{:2d}/{:1d}".format(li_short, li_extended, fthr_gpsi.i_sat_in_view, fthr_gpsi.i_sat_used), M_LIN_ADS, 0)

        # sleep (update each 4s)
        time.sleep(4)

# -------------------------------------------------------------------------------------------------
def main():
    """
    drive app
    """
    # create sys.arg parser
    l_parser = argparse.ArgumentParser()
    assert l_parser

    # parser options
    l_parser.add_argument("--display", dest="display", action="store_true", help="enable LCD display output")
    l_parser.add_argument("--no-display", dest="display", action="store_false", help="disable LCD display")
    l_parser.set_defaults(display=True)

    # get arguments
    l_args = l_parser.parse_args()

    # hostname
    ls_host = os.uname()[1]

    # data atual
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

    # create thread update display
    lthr_upd_dsp = threading.Thread(target=update_display, args=(lthr_gpsi, lthr_adsi, l_args.display))
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
            # sleep 4s
            time.sleep(4)

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
