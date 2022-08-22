#!/usr/bin/env python3

import sys, os, time
import serial

from flipperzero_protobuf_py.flipper_protobuf import ProtoFlipper
from flipperzero_protobuf_py.flipperzero_protobuf_compiled import flipper_pb2, system_pb2
from flipperzero_protobuf_py.cli_helpers import *

def flp_exec_cmd(proto, cmd):
    if cmd == 'alert':
        proto.cmd_system_audiovisual_alert()
    elif cmd == 'ping':
        if proto.cmd_system_ping() == b'\xde\xad\xbe\xef':
            print('pong')
        else:
            print('ping error', file=sys.stderr)
    elif cmd == 'up':
        proto.cmd_gui_send_input("SHORT UP")
    elif cmd == 'dn':
        proto.cmd_gui_send_input("SHORT DOWN")
    elif cmd == 'lt':
        proto.cmd_gui_send_input("SHORT LEFT")
    elif cmd == 'rt':
        proto.cmd_gui_send_input("SHORT RIGHT")
    elif cmd == 'ok':
        proto.cmd_gui_send_input("SHORT OK")
    elif cmd == 'bk':
        proto.cmd_gui_send_input("SHORT BACK")
    elif cmd == 'screen':
        print_screen(proto.cmd_gui_snapshot_screen())
    elif cmd == 'exit':
        proto.cmd_app_exit()
    elif cmd == 's1':
        time.sleep(1)
    elif cmd == 'reboot':
        proto.cmd_reboot_os()
    elif cmd == 'dfu':
        proto.cmd_reboot_dfu()
    elif cmd == 'update':
        proto.cmd_reboot_update()
    else:
        print("Unknown command " + cmd, file=sys.stderr)

def flp_exec_cmds(proto, cmds):
    for cmd in cmds:
        flp_exec_cmd(proto, cmd)

def flp_serial_by_name(flp_name):
    if sys.platform == 'darwin':    #MacOS
        flp_serial = '/dev/cu.usbmodemflip_' + flp_name + '1'
    elif sys.platform == 'linux':   #Linux
        flp_serial = '/dev/serial/by-id/usb-Flipper_Devices_Inc._Flipper_' + flp_name + '_flip_' + flp_name + '-if00'

    if os.path.exists(flp_serial):
        return flp_serial
    else:
        if os.path.exists(flp_name):
            return flp_name
        else:
            return ''

class ProtoFlipperExt(ProtoFlipper):
    def cmd_reboot_os(self):
        """Reboot flipper OS"""
        cmd_data = system_pb2.RebootRequest()
        cmd_data.mode = system_pb2.RebootRequest.RebootMode.OS
        data = self._cmd_send_and_read_answer(
            cmd_data, 'system_reboot_request')
        return data
    def cmd_reboot_dfu(self):
        """Reboot flipper to DFU"""
        cmd_data = system_pb2.RebootRequest()
        cmd_data.mode = system_pb2.RebootRequest.RebootMode.DFU
        data = self._cmd_send_and_read_answer(
            cmd_data, 'system_reboot_request')
        return data
    def cmd_reboot_update(self):
        """Reboot flipper to Update"""
        cmd_data = system_pb2.RebootRequest()
        cmd_data.mode = system_pb2.RebootRequest.RebootMode.UPDATE
        data = self._cmd_send_and_read_answer(
            cmd_data, 'system_reboot_request')
        return data

def main():
    flp_serial = flp_serial_by_name(sys.argv[1])

    if flp_serial == '':
        print("Name or serial port is invalid")
        sys.exit(1)
    
    flipper = serial.Serial(flp_serial, timeout=1)
    flipper.baudrate = 230400
    flipper.flushOutput()
    flipper.flushInput()

    flipper.timeout = None

    flipper.read_until(b'>: ')

    flipper.write(b"start_rpc_session\r")
    flipper.read_until(b'\n')

    #proto = ProtoFlipper(flipper)
    proto = ProtoFlipperExt(flipper)

    flp_exec_cmds(proto, sys.argv[2:])

if __name__ == '__main__':
    main()
