#!/usr/bin/env python3

import numpy
import os
import sys
import asyncio
import keyboard
import logging

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Setting up the current directory and import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'flipperzero_protobuf_py'))

# Import necessary classes and functions
from async_protopy.commands.gui_commands import StartScreenStreamRequestCommand

SCREEN_H = 128
SCREEN_W = 64

# ANSI escape codes for setting color
BLACK_ON_ORANGE = "\033[30;48;5;208m"
RESET_COLOR = "\033[0m"

shutdown_flag = False  # Flag to terminate the program


def get_bin(x):
    return format(x, 'b')


def print_screen_braille(screen_bytes, return_output=False):
    data = screen_bytes
    scr = numpy.zeros((SCREEN_W, SCREEN_H))

    x = y = 0
    basex = 0

    for i in range(0, int(SCREEN_H * SCREEN_W / 8)):
        tmp = get_bin(data[i])
        tmp = '0' * (8 - len(tmp)) + tmp
        tmp = tmp[::-1]

        x = basex
        y += 1

        for c in tmp:
            scr[x][y % SCREEN_H] = int(c)
            x += 1

        if (i + 1) % SCREEN_H == 0:
            basex += 8
            y = 0

    output = []

    for j in range(0, SCREEN_W, 4):
        line = []

        for i in range(1, SCREEN_H, 2):
            v = 0

            for k in range(8):
                x = j
                y = i
                
                if k <= 2:
                    x += k
                elif k <= 5:
                    y += 1
                    x += k - 3
                elif k == 6:
                    x += 3
                else:
                    y += 1
                    x += 3

                if x < SCREEN_W and y < SCREEN_H and scr[x][y]:
                    v |= (1 << k)

            braille_char = chr(0x2800 + v)
            line.append(braille_char)

        output.append(''.join(line))

    if return_output:
        return '\n'.join(output)
    else:
        print('\n'.join(output))


def print_screen(screen_bytes, last_scr=None):
    data = screen_bytes
    scr = numpy.zeros((SCREEN_H + 1, SCREEN_W + 1))

    x = y = 0
    basey = 0

    for i in range(0, int(SCREEN_H * SCREEN_W / 8)):
        tmp = format(data[i], '08b')[::-1]  # Get binary representation and reverse

        y = basey
        x += 1
        for c in tmp:
            scr[x][y] = int(c)
            y += 1

        if (i + 1) % SCREEN_H == 0:
            basey += 8
            x = 0

    # Compare with the last frame and only update changes
    if last_scr is not None:
        for y in range(0, SCREEN_W, 2):
            for x in range(1, SCREEN_H + 1):
                current_pixel = (int(scr[x][y]), int(scr[x][y + 1]))
                last_pixel = (int(last_scr[x][y]), int(last_scr[x][y + 1]))

                if current_pixel != last_pixel:
                    # Move cursor to the correct position and update only the changed character
                    print(f"\033[{x};{y//2}H", end='')  # Move cursor to x, y//2
                    if current_pixel == (1, 1):
                        print(u'\u2588', end='')  # Full block
                    elif current_pixel == (0, 1):
                        print(u'\u2584', end='')  # Lower half block
                    elif current_pixel == (1, 0):
                        print(u'\u2580', end='')  # Upper half block
                    else:
                        print(' ', end='')  # Space
    else:
        # Full screen update if last_scr is None (first frame)
        for y in range(0, SCREEN_W, 2):
            for x in range(1, SCREEN_H + 1):
                if int(scr[x][y]) == 1 and int(scr[x][y + 1]) == 1:
                    print(u'\u2588', end='')  # Full block
                elif int(scr[x][y]) == 0 and int(scr[x][y + 1]) == 1:
                    print(u'\u2584', end='')  # Lower half block
                elif int(scr[x][y]) == 1 and int(scr[x][y + 1]) == 0:
                    print(u'\u2580', end='')  # Upper half block
                else:
                    print(' ', end='')  # Space
            print()

    return scr  # Return the current frame for comparison in the next iteration


async def send_input_event(proto, key, itype):
    """Send an input event to Flipper Zero with error logging."""
    try:
        await proto.gui.send_input_event_request(key=key, itype=itype)
    except Exception as e:
        logging.error(f"Error sending input event: {e}")


async def send_command_sequence(proto, key, duration):
    await send_input_event(proto, key, "PRESS")
    await send_input_event(proto, key, duration)
    await send_input_event(proto, key, "RELEASE")


async def handle_keypress(proto):
    """Function to handle key presses."""
    global shutdown_flag
    loop = asyncio.get_event_loop()

    def on_key_event(event):
        global shutdown_flag
        key = event.scan_code
        shift_pressed = keyboard.is_pressed('shift') or keyboard.is_pressed('right shift')

        commands = {
            17: "UP", 72: "UP",
            31: "DOWN", 80: "DOWN",
            30: "LEFT", 75: "LEFT",
            32: "RIGHT", 77: "RIGHT",
            37: "OK", 57: "OK",
            48: "BACK", 46: "BACK"
        }

        if key in commands:
            duration = "LONG" if shift_pressed else "SHORT"
            loop.create_task(send_command_sequence(proto, commands[key], duration))
        elif key == 16:  # Terminate the program
            shutdown_flag = True

    # Set up keyboard event handlers
    keyboard.on_press(on_key_event)

    # Main program loop
    while not shutdown_flag:
        await asyncio.sleep(0.1)

    # Remove keyboard event handlers and clear buffer
    keyboard.unhook_all()
    keyboard.clear_all_hotkeys()


async def stream_screen(proto, display_function):
    stream_response = await proto.stream(StartScreenStreamRequestCommand(), command_id=0)
    last_data = None

    async for data in stream_response:
        if shutdown_flag:
            break

        if not data.gui_screen_frame.data:
            continue

        scrbytes = data.gui_screen_frame.data

        if len(scrbytes) % 2 != 0 or (last_data and last_data.gui_screen_frame.data == scrbytes):
            continue

        if last_data:
            for i in range(len(scrbytes)):
                if scrbytes[i] != last_data.gui_screen_frame.data[i]:
                    print("\033[H\033[J", end='')  # Clear screen
                    print(BLACK_ON_ORANGE, end='')
                    display_function(scrbytes)
                    print(RESET_COLOR, end='')
                    break
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\033[H\033[J", end='')
            print(BLACK_ON_ORANGE, end='')
            display_function(scrbytes)
            print(RESET_COLOR, end='')

        last_data = data

# Main function to run the program
async def main():
    # Initialize proto and call handle_keypress and stream_screen here
    pass

if __name__ == "__main__":
    asyncio.run(main())