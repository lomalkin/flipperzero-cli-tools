#!/usr/bin/env python3
import sys
import os
import platform
import asyncio
import argparse
from pynput import keyboard
from serial.serialutil import SerialException

if platform.system() == "Windows":
    import msvcrt

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'flipperzero_protobuf_py'))

from flipperzero_protobuf_py.async_protopy.clients.protobuf_client import FlipperProtobufClient
from flipperzero_protobuf_py.async_protopy.connectors.serial_connector import SerialConnector
from flipperzero_protobuf_py.async_protopy.flipperzero_protobuf_compiled import gui_pb2
from src.helpers import flipper_serial_by_name

# Импортируем классы с функционалом
from src.cli_helpers import setup_helpers

flipper_helper, display_helper = setup_helpers()

async def main():
    parser = argparse.ArgumentParser(description="Stream screen from Flipper Zero to terminal.")
    parser.add_argument('port', help="Serial port to connect to (e.g., COM5).")
    parser.add_argument('mode', nargs='?', default='unicode', 
                        help="Display mode: 'braille' for Braille, 'unicode' (default) for Unicode.")
    
    args = parser.parse_args()

    flp_serial = flipper_serial_by_name(args.port)
    if not flp_serial:
        print("Name or serial port is invalid")
        sys.exit(1)

    use_braille = args.mode == 'braille'
    running_event = asyncio.Event()
    running_event.set()

    try:
        async with FlipperProtobufClient(SerialConnector(url=flp_serial, baud_rate=230400)) as proto:
            flipper_helper.disable_input()

            commands = {
                keyboard.Key.up: gui_pb2.InputKey.UP,
                keyboard.Key.down: gui_pb2.InputKey.DOWN,
                keyboard.Key.left: gui_pb2.InputKey.LEFT,
                keyboard.Key.right: gui_pb2.InputKey.RIGHT,
                keyboard.Key.enter: gui_pb2.InputKey.OK,
                keyboard.Key.backspace: gui_pb2.InputKey.BACK,
                keyboard.Key.delete: gui_pb2.InputKey.BACK
            }

            loop = asyncio.get_running_loop()

            with keyboard.Listener(
                    on_press=lambda key: flipper_helper.on_press(key, proto, commands, loop, running_event),
                    on_release=flipper_helper.on_release) as listener:

                await asyncio.gather(
                    flipper_helper.handle_flipper_commands(proto),
                    flipper_helper.stream_screen(proto, display_helper.print_screen_braille if use_braille else display_helper.print_screen),
                    flipper_helper.wait_for_exit(running_event)
                )
                listener.join()

    except SerialException as e:
        print(f"Error opening serial port: {e}")
    finally:
        if platform.system() == "Windows":
            flipper_helper.clear_windows_input_buffer()
        flipper_helper.enable_input()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        flipper_helper.shutdown_program()
