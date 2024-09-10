#!/usr/bin/env python3

import logging
import os
import sys
import asyncio
import keyboard
import argparse
from serial.serialutil import SerialException

# Setting up the current directory and import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'flipperzero_protobuf_py'))

# Import necessary classes and functions from your library
from async_protopy.clients.protobuf_client import FlipperProtobufClient
from async_protopy.connectors.serial_connector import SerialConnector
from src.cli_helpers import print_screen, print_screen_braille, handle_keypress, stream_screen

async def stream_screen_braille(proto):
    """Function to display the screen using Braille."""
    await stream_screen(proto, lambda scrbytes: print(print_screen_braille(scrbytes, True)))

async def stream_screen_unicode(proto):
    """Function to display the screen using Unicode."""
    await stream_screen(proto, print_screen)


async def main():
    global shutdown_flag

    parser = argparse.ArgumentParser(description="Stream screen from Flipper Zero to terminal.")
    parser.add_argument('port', help="Serial port to connect to (e.g., COM5).")
    parser.add_argument('mode', nargs='?', default='unicode', 
                        help="Display mode: 'braille' for Braille, 'unicode' (default) for Unicode.")
    
    args = parser.parse_args()

    flp_serial = args.port

    try:
        async with FlipperProtobufClient(SerialConnector(url=flp_serial, baud_rate=230400)) as proto:
            # Select streaming mode (Braille or Unicode)
            if args.mode == 'braille':
                await asyncio.gather(
                    handle_keypress(proto),     # Handle key presses
                    stream_screen_braille(proto)  # Stream screen in Braille
                )
            else:
                await asyncio.gather(
                    handle_keypress(proto),     # Handle key presses
                    stream_screen_unicode(proto)  # Stream screen in Unicode
                )
    except SerialException as e:
        logging.error(f"SerialException: failed to open port {flp_serial}: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
    except Exception as e:
        print(f"Error in the main program: {e}", exc_info=True)
    finally:
        keyboard.unhook_all()
        print("Flipper ending completed.")
        sys.exit(0)  # Forcefully terminate the program