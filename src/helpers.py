import numpy
import sys, os

def flipper_serial_by_name(flp_name):
    flp_serial = None  # Инициализация переменной
    if sys.platform == 'darwin':    # MacOS
        flp_serial = '/dev/cu.usbmodemflip_' + flp_name + '1'
    elif sys.platform == 'linux':   # Linux
        flp_serial = '/dev/serial/by-id/usb-Flipper_Devices_Inc._Flipper_' + flp_name + '_flip_' + flp_name + '-if00'
    elif sys.platform == 'win32':   # Windows
        flp_serial = '\\\\.\\' + flp_name

    if flp_serial and os.path.exists(flp_serial):
        return flp_serial
    else:
        if os.path.exists(flp_name):
            return flp_name
        else:
            return ''

def print_lines_in_one_place(lines):
    # Usage: print "\r" * len(lines) first,
    # to reserve space for lines
    sys.stdout.write(
        f"\033[F\033[K" * len(lines)
    )  # move cursor up one line, clear line, repeat
    for line in lines:
        sys.stdout.write(line)
        sys.stdout.write("\n")
    sys.stdout.flush()

def print_screen_braille3(screen_bytes, return_output=False):
    SCREEN_H = 128
    SCREEN_W = 64

    data = screen_bytes
    def get_bin(x): return format(x, 'b')
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