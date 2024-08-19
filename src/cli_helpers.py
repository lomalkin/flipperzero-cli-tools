#!/usr/bin/env python3

import numpy


def print_hex(bytes_data):
    print("".join('{:02x} '.format(x) for x in bytes_data))


def print_screen(screen_bytes):
    SCREEN_H = 128
    SCREEN_W = 64

    data = screen_bytes
    def get_bin(x): return format(x, 'b')
    scr = numpy.zeros((SCREEN_H+1, SCREEN_W+1))

    x = y = 0
    basey = 0

    for i in range(0, int(SCREEN_H*SCREEN_W/8)):
        tmp = get_bin(data[i])
        tmp = '0'*(8-len(tmp)) + tmp
        tmp = tmp[::-1]  # reverse

        y = basey
        x += 1
        for c in tmp:
            scr[x][y] = c
            y += 1

        if (i + 1) % SCREEN_H == 0:
            basey += 8
            x = 0

    for y in range(0, SCREEN_W, 2):
        for x in range(1, SCREEN_H+1):
            if int(scr[x][y]) == 1 and int(scr[x][y+1]) == 1:
                print(u'\u2588', end='')
            if int(scr[x][y]) == 0 and int(scr[x][y+1]) == 1:
                print(u'\u2584', end='')
            if int(scr[x][y]) == 1 and int(scr[x][y+1]) == 0:
                print(u'\u2580', end='')
            if int(scr[x][y]) == 0 and int(scr[x][y+1]) == 0:
                print(' ', end='')
        print()






