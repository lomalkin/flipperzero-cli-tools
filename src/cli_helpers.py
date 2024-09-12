import numpy
import os
import sys
import asyncio
import platform
import shutil
import traceback
from pynput import keyboard
from async_protopy.commands.gui_commands import StartScreenStreamRequestCommand
from async_protopy.flipperzero_protobuf_compiled import gui_pb2

if platform.system() == "Windows":
    import msvcrt
else:
    import termios

# Логика для работы с вводом и Flipper в виде классов
class FlipperHelper:
    
    def __init__(self):
        self.shift_pressed = False
        self.shutdown_flag = False
        self.old_termios = None
        # ANSI цвета для фона
        self.BLACK_ON_ORANGE = "\033[30;48;5;208m"
        self.RESET_COLOR = "\033[0m"

    def disable_input(self):
        """Disable input based on OS."""
        if platform.system() == "Windows":
            pass
        else:
            self.old_termios = termios.tcgetattr(sys.stdin)  # Save terminal settings
            tty_attr = termios.tcgetattr(sys.stdin)
            tty_attr[3] = tty_attr[3] & ~(termios.ICANON | termios.ECHO)  # Disable canonical mode and echo
            termios.tcsetattr(sys.stdin, termios.TCSANOW, tty_attr)  # Apply new attributes
            os.system('stty -echo')  # Disable echo

    def enable_input(self):
        """Enable input based on OS."""
        if platform.system() == "Windows":
            pass
        else:
            termios.tcsetattr(sys.stdin, termios.TCSANOW, self.old_termios)  # Restore terminal settings
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)  # Flush buffers
            os.system('stty echo')  # Enable echo

    def clear_windows_input_buffer(self):
        """Clears the input buffer on Windows."""
        while msvcrt.kbhit():
            msvcrt.getch()

    def on_press(self, key, proto, commands, loop, running_event):
        """Handle key press event."""
        try:
            if key in (keyboard.Key.shift, keyboard.Key.shift_r):
                self.shift_pressed = True

            if key in commands:
                duration_type = gui_pb2.InputType.LONG if self.shift_pressed else gui_pb2.InputType.SHORT
                asyncio.run_coroutine_threadsafe(self.send_command_to_flipper(proto, commands[key], duration_type), loop)

            if key == keyboard.Key.esc:
                running_event.clear()
                self.shutdown_program()  # Terminate the program
                return False  # Stop listener

        except Exception as e:
            print(f"Error: {e}")
            running_event.clear()
            self.shutdown_program()  # Terminate the program
            return False

    def on_release(self, key):
        if key in (keyboard.Key.shift, keyboard.Key.shift_r):
            self.shift_pressed = False

    async def handle_flipper_commands(self, proto):
        """Asynchronous function for handling Flipper commands."""
        try:
            while True:
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in Flipper handling: {e}")
            traceback.print_exc()

    async def send_command_to_flipper(self, proto, key, duration_type):
        """Send command to Flipper."""
        try:
            key_str = gui_pb2.InputKey.Name(key)
            type_str = gui_pb2.InputType.Name(duration_type)

            await proto.gui.send_input_event_request(key=key_str, itype="PRESS")
            await proto.gui.send_input_event_request(key=key_str, itype=type_str)
            await proto.gui.send_input_event_request(key=key_str, itype="RELEASE")
        except Exception as e:
            print(f"Error sending command to Flipper: {e}")
            traceback.print_exc()

    def display_manual_below_screen(self):
        """Display control manual below the screen."""
        columns, rows = shutil.get_terminal_size()
        print(f"{self.BLACK_ON_ORANGE}Controls: Arrows - D-pad, Enter - OK, Backspace/Delete - BACK, key+shift - long press, Esc - quit{self.RESET_COLOR}")

    async def stream_screen(self, proto, display_function):
        """Stream screen from Flipper."""
        stream_response = await proto.stream(StartScreenStreamRequestCommand(), command_id=0)
        last_data = None

        async for data in stream_response:
            if self.shutdown_flag:
                break

            if not data.gui_screen_frame.data:
                continue

            scrbytes = data.gui_screen_frame.data

            if len(scrbytes) % 2 != 0 or (last_data and last_data.gui_screen_frame.data == scrbytes):
                continue

            # Устанавливаем оранжевый фон
            print(f"\033[H\033[J{self.BLACK_ON_ORANGE}", end='')  # Clear the screen and set orange background
            display_function(scrbytes)  # Display screen data

            # Отображаем инструкцию внизу экрана
            self.display_manual_below_screen()

            last_data = data

    async def wait_for_exit(self, running_event):
        await running_event.wait()

    def shutdown_program(self):
        print("Shutting down the program.")
        self.enable_input()
        os._exit(0)

# Логика для отображения
class DisplayHelper:
    
    SCREEN_H = 128
    SCREEN_W = 64

    def __init__(self):
        pass

    def print_screen_braille(self, screen_bytes, return_output=False):
        """Display screen in Braille mode."""
        data = screen_bytes
        scr = numpy.zeros((self.SCREEN_W, self.SCREEN_H))

        x = y = 0
        basex = 0

        for i in range(0, int(self.SCREEN_H * self.SCREEN_W / 8)):
            tmp = format(data[i], '08b')[::-1]  # Get binary representation and reverse it

            x = basex
            y += 1

            for c in tmp:
                scr[x][y % self.SCREEN_H] = int(c)
                x += 1

            if (i + 1) % self.SCREEN_H == 0:
                basex += 8
                y = 0

        output = []

        for j in range(0, self.SCREEN_W, 4):
            line = []

            for i in range(1, self.SCREEN_H, 2):
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

                    if x < self.SCREEN_W and y < self.SCREEN_H and scr[x][y]:
                        v |= (1 << k)

                braille_char = chr(0x2800 + v)
                line.append(braille_char)

            output.append(''.join(line))

        if return_output:
            return '\n'.join(output)
        else:
            print('\n'.join(output))

    def print_screen(self, screen_bytes, last_scr=None):
        """Display screen in Unicode mode."""
        data = screen_bytes
        scr = numpy.zeros((self.SCREEN_H + 1, self.SCREEN_W + 1))

        x = y = 0
        basey = 0

        for i in range(0, int(self.SCREEN_H * self.SCREEN_W / 8)):
            tmp = format(data[i], '08b')[::-1]  # Get binary representation and reverse it

            y = basey
            x += 1
            for c in tmp:
                scr[x][y] = int(c)
                y += 1

            if (i + 1) % self.SCREEN_H == 0:
                basey += 8
                x = 0

        if last_scr is not None:
            for y in range(0, self.SCREEN_W, 2):
                for x in range(1, self.SCREEN_H + 1):
                    current_pixel = (int(scr[x][y]), int(scr[x][y + 1]))
                    last_pixel = (int(last_scr[x][y]), int(last_scr[x][y + 1]))

                    if current_pixel != last_pixel:
                        print(f"\033[{x};{y//2}H", end='')  # Move cursor to position x, y//2
                        if current_pixel == (1, 1):
                            print(u'\u2588', end='')  # Full block
                        elif current_pixel == (0, 1):
                            print(u'\u2584', end='')  # Lower half block
                        elif current_pixel == (1, 0):
                            print(u'\u2580', end='')  # Upper half block
                        else:
                            print(' ', end='')  # Space
        else:
            for y in range(0, self.SCREEN_W, 2):
                for x in range(1, self.SCREEN_H + 1):
                    if int(scr[x][y]) == 1 and int(scr[x][y + 1]) == 1:
                        print(u'\u2588', end='')  # Full block
                    elif int(scr[x][y]) == 0 and int(scr[x][y + 1]) == 1:
                        print(u'\u2584', end='')  # Lower half block
                    elif int(scr[x][y]) == 1 and int(scr[x][y + 1]) == 0:
                        print(u'\u2580', end='')  # Upper half block
                    else:
                        print(' ', end='')  # Space
                print()

        return scr  # Return the current image for comparison in the next step

# Экспортируем необходимые функции
def setup_helpers():
    return FlipperHelper(), DisplayHelper()
