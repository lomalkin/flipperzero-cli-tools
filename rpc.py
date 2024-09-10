#!/usr/bin/env python3

import sys, os, time
import asyncio
import serial_asyncio

# Добавление пути к модулю flipperzero_protobuf_py
current_dir = os.path.dirname(os.path.abspath(__file__))
flipper_protobuf_path = os.path.join(current_dir, 'flipperzero_protobuf_py')
if flipper_protobuf_path not in sys.path:
    sys.path.append(flipper_protobuf_path)

from flipperzero_protobuf_py.flipper_protobuf import ProtoFlipper
from flipperzero_protobuf_py.flipperzero_protobuf_compiled import flipper_pb2, system_pb2
from src.cli_helpers import *
from src.helpers import print_screen_braille3 as print_screen_braille, flipper_serial_by_name

async def flp_exec_cmd(proto, cmd):
    if cmd == 'alert':
        await proto.cmd_system_audiovisual_alert()
    elif cmd == 'ping':
        if await proto.cmd_system_ping() == b'\xde\xad\xbe\xef':
            print('pong')
        else:
            print('ping error', file=sys.stderr)
    elif cmd == 'up':
        await proto.cmd_gui_send_input("SHORT UP")
    elif cmd == 'dn':
        await proto.cmd_gui_send_input("SHORT DOWN")
    elif cmd == 'lt':
        await proto.cmd_gui_send_input("SHORT LEFT")
    elif cmd == 'rt':
        await proto.cmd_gui_send_input("SHORT RIGHT")
    elif cmd == 'ok':
        await proto.cmd_gui_send_input("SHORT OK")
    elif cmd == 'bk':
        await proto.cmd_gui_send_input("SHORT BACK")
    elif cmd == 'screen':
        print_screen(await proto.cmd_gui_snapshot_screen())
    elif cmd == 'screen_braille':
        print_screen_braille(await proto.cmd_gui_snapshot_screen())
    elif cmd == 'exit':
        await proto.cmd_app_exit()
    elif cmd == 's1':
        await asyncio.sleep(1)
    elif cmd == 'reboot':
        await proto.cmd_reboot_os()
    elif cmd == 'dfu':
        await proto.cmd_reboot_dfu()
    elif cmd == 'update':
        await proto.cmd_reboot_update()
    else:
        print("Unknown command " + cmd, file=sys.stderr)

async def flp_exec_cmds(proto, cmds):
    for cmd in cmds:
        await flp_exec_cmd(proto, cmd)

class ProtoFlipperExt(ProtoFlipper):
    async def cmd_reboot_os(self):
        """Reboot flipper OS"""
        cmd_data = system_pb2.RebootRequest()
        cmd_data.mode = system_pb2.RebootRequest.RebootMode.OS
        data = await self._cmd_send_and_read_answer(
            cmd_data, 'system_reboot_request')
        return data

    async def cmd_reboot_dfu(self):
        """Reboot flipper to DFU"""
        cmd_data = system_pb2.RebootRequest()
        cmd_data.mode = system_pb2.RebootRequest.RebootMode.DFU
        data = await self._cmd_send_and_read_answer(
            cmd_data, 'system_reboot_request')
        return data

    async def cmd_reboot_update(self):
        """Reboot flipper to Update"""
        cmd_data = system_pb2.RebootRequest()
        cmd_data.mode = system_pb2.RebootRequest.RebootMode.UPDATE
        data = await self._cmd_send_and_read_answer(
            cmd_data, 'system_reboot_request')
        return data

async def main():
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " <name or serial port>")
        sys.exit(1)

    flp_serial = flipper_serial_by_name(sys.argv[1])
    if flp_serial == '':
        print("Name or serial port is invalid")
        sys.exit(1)
    
    reader, writer = await serial_asyncio.open_serial_connection(url=flp_serial, baudrate=230400)

    writer.write(b"start_rpc_session\r")
    await reader.readuntil(b'\n')

    proto = ProtoFlipperExt(reader, writer)

    await flp_exec_cmds(proto, sys.argv[2:])

if __name__ == '__main__':
    asyncio.run(main())