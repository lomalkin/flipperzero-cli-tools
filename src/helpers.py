#!/usr/bin/env python3

import sys
import os
import serial.tools.list_ports

def flipper_serial_by_name(flp_name):
    flp_serial = None

    if sys.platform == 'darwin':    # MacOS
        flp_serial = '/dev/cu.usbmodemflip_' + flp_name + '1'
    elif sys.platform == 'linux':   # Linux
        flp_serial = '/dev/serial/by-id/usb-Flipper_Devices_Inc._Flipper_' + flp_name + '_flip_' + flp_name + '-if00'
    elif sys.platform == 'win32':   # Windows
        # List all available serial ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if flp_name in port.description:
                flp_serial = port.device
                break

    if flp_serial and os.path.exists(flp_serial):
        return flp_serial
    else:
        if os.path.exists(flp_name):
            return flp_name
        else:
            return ''