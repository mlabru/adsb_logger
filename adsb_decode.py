#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------------------------------
adsb_decode

revision 0.3  2017/nov  mlabru
RPi data logger mods

revision 0.2  2015/nov  mlabru
pep8 style conventions

revision 0.1  2014/nov  mlabru
initial version (Linux/Python)
---------------------------------------------------------------------------------------------------
"""
__version__ = "$revision: 0.3$"
__author__ = "mlabru, sophosoft"
__date__ = "2017/11"

# < imports >--------------------------------------------------------------------------------------

# python library
import logging
import time

import adsb_decoder as dcdr

# < module data >----------------------------------------------------------------------------------

# logger
M_LOG = logging.getLogger(__name__)
M_LOG.setLevel(logging.DEBUG)

# -------------------------------------------------------------------------------------------------
# dicionário de cpr's
dct_cpr = {}

# -------------------------------------------------------------------------------------------------
def decode_adsb(fs_msg):
    """
    decode message

    @param fs_msg: message to decode
    """
    # logger
    # M_LOG.info(">> decode_adsb")

    # invalid message ?
    if not (fs_msg.startswith('*') and fs_msg.endswith(';')):
        # logger
        M_LOG.warning("decode_adsb:<E01: invalid message [{}]".format(fs_msg))

        # return
        return

    # obtém a mensagem em hexadecimal
    ls_hex_message = fs_msg[1:-2]
    M_LOG.debug("ls_hex_message: {}".format(ls_hex_message))

    #if not dcdr.checksum(ls_hex_message):
        #M_LOG.debug("decode_adsb:Erro de checksum !!!")
        #return

    # calcula o tamanho da mensagem em binário
    ln_bits = 4 * len(ls_hex_message)

    # obtém a mensagem em binário
    ls_bin_message = bin(int(ls_hex_message, 16))[2:].zfill(ln_bits)

    # downlink format
    li_df = int(ls_bin_message[0:5], 2)

    # mensagem ADS-B tratável ?
    if li_df not in [ 17 ]:
        # logger
        M_LOG.warning("decode_adsb:<E02: tipo de mensagem não tratada.")

        # return
        return

    # message subtype / capability (3 bits) (get_cap)
    li_cap = int(ls_bin_message[5:8], 2)

    # ICAO aircraft address (get_icao_addr)
    ls_icao_addr = ls_hex_message[2:8]

    # CRC (error check)
    ls_crc = ls_hex_message[-6:]
    M_LOG.debug("ls_crc: {}".format(ls_crc))

    # extended squitter type (get_tc)
    li_type_code = int(ls_bin_message[32:37], 2)

    try:
        # aircraft identification
        if li_type_code in xrange(1, 5):

            M_LOG.debug("aircraft identification")

            # aircraft category (3 bits)
            li_type = int(ls_bin_message[38:40], 2)
            M_LOG.debug("li_type: {}".format(li_type))

            # atualiza o callsign na aeronave
            s_callsign = dcdr.get_callsign(ls_bin_message)

        # surface position
        elif li_type_code in xrange(5, 9):
            M_LOG.debug("surface position")
            pass

        # airborne position
        elif li_type_code in xrange(9, 19):

            M_LOG.debug("airborne position (Baro Alt)")

            # surveillance status (2 bits)
            #
            # - 0 no emergency or other Mode 3/A code information
            # - 1 permanent alert (emergency code)
            # - 2 temporary alert (change of Mode 3/A code other than emergency)
            # - 3 special position indicator (SPI) condition

            sv_status = int(ls_bin_message[37:39], 2)
            M_LOG.debug("sv_status: {}".format(sv_status))

            # altitude (12 bits) (get_alt)
            altitude = dcdr.get_alt(ls_bin_message)
            M_LOG.debug("altitude: {}".format(altitude))

            # CPR odd/even flag (1 bit) (get_oe_flag)
            cpr_format_flag = int(ls_bin_message[53])

            if 1 == cpr_format_flag:
                if (ls_icao_addr in dct_cpr) and (dct_cpr[ls_icao_addr] is not None):
                    lat, lng = dcdr.cpr2position(dcdr.get_cprlat(dct_cpr[ls_icao_addr]),
                                                 dcdr.get_cprlat(ls_bin_message),
                                                 dcdr.get_cprlng(dct_cpr[ls_icao_addr]),
                                                 dcdr.get_cprlng(ls_bin_message), 0, 1)
                    M_LOG.debug(">>>>>>>>>>>>>>  lat, lng: {}".format((lat, lng)))

                dct_cpr[ls_icao_addr] = None

            elif 0 == cpr_format_flag:
                dct_cpr[ls_icao_addr] = ls_bin_message

        # airborne velocities ?
        elif 19 == li_type_code:

            M_LOG.debug("airborne velocities")

            # extended squitter subtype
            es_subtype = int(ls_bin_message[38:40], 2)
            M_LOG.debug("es_subtype: {}".format(es_subtype))

            # obtém a velocidade e a proa
            l_vel, l_proa = dcdr.get_speed_heading(ls_bin_message)
            M_LOG.debug("speed, heading: {}".format((l_vel, l_proa)))

            # turn indicator (2-bit)
            turn_indicator = int(ls_bin_message[78:79], 2)
            M_LOG.debug("turn_indicator: {}".format(turn_indicator))

        # airborne position (GNSS height) ?
        elif li_type_code in xrange(20, 23):
            M_LOG.debug("airborne position (GNSS height)")
            pass

        # test message ?
        elif 23 == li_type_code:
            M_LOG.debug("test message")
            pass

        # surface system status ?
        elif 24 == li_type_code:
            M_LOG.debug("surface system status")
            pass

        # reserved ?
        elif li_type_code in xrange(25, 28):
            M_LOG.debug("reserved")
            pass

        # extended squitter AC status ?
        elif 28 == li_type_code:
            M_LOG.debug("extended squitter AC status")
            pass

        # target state and status (V.2) ?
        elif 29 == li_type_code:
            M_LOG.debug("target state and status (V.2)")
            pass

        # reserved ?
        elif 30 == li_type_code:
            M_LOG.debug("reserved")
            pass

        # aircraft operation status ?
        elif 31 == li_type_code:
            M_LOG.debug("aircraft operation status")
            pass

        # senão,...
        else:
            # logger
            l_log = logging.getLogger("CEmulaVisADSB::decode_adsb")
            l_log.setLevel(logging.NOTSET)
            l_log.warning("E01: mensagem não reconhecida ou não tratada.")

    except: pass

# < the end >--------------------------------------------------------------------------------------
