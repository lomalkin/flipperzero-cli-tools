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


def print_screen_braille(screen_bytes):
    SCREEN_H = 128
    SCREEN_W = 64

    data = screen_bytes
    def get_bin(x): return format(x, 'b')
    scr = numpy.zeros((SCREEN_W, SCREEN_H))

    x = y = 0
    basex = 0

    for i in range(0, int(SCREEN_H*SCREEN_W/8)):
        tmp = get_bin(data[i])
        tmp = '0'*(8-len(tmp)) + tmp
        tmp = tmp[::-1]  # reverse

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
        for i in range(0, SCREEN_H, 2):
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

    print('\n'.join(output))














def print_screen_braille2(screen_bytes):
    SCREEN_H = 128  # Высота экрана в пикселях
    SCREEN_W = 64   # Ширина экрана в пикселях

    data = screen_bytes
    def get_bin(x): return format(x, 'b')  # Функция для преобразования числа в двоичное представление
    scr = numpy.zeros((SCREEN_W, SCREEN_H))  # Создаем пустую матрицу для хранения битов экрана

    x = y = 0  # Инициализация координат
    basex = 0  # Базовое значение для координаты x

    # Проход по каждому байту данных экрана
    for i in range(0, int(SCREEN_H * SCREEN_W / 8)):
        tmp = get_bin(data[i])  # Преобразование байта в двоичный формат
        tmp = '0' * (8 - len(tmp)) + tmp  # Дополнение строки нулями до 8 бит
        tmp = tmp[::-1]  # Зеркальное разворачивание строки (инверсия)

        x = basex  # Установка начальной позиции x
        y += 1  # Переход к следующей позиции y

        # Запись битов в матрицу scr
        for c in tmp:
            scr[x][y % SCREEN_H] = int(c)  # Записываем бит в матрицу scr
            x += 1  # Сдвигаем x вправо

        # Обновление базового значения x и сброс y после каждых 8 байтов
        if (i + 1) % SCREEN_H == 0:
            basex += 8
            y = 0

    output = []  # Список для хранения строк вывода

    # Проход по ширине экрана с шагом 4 пикселя
    for j in range(0, SCREEN_W, 4):
        line = []  # Список для хранения символов одной строки

        # Проход по высоте экрана с шагом 2 пикселя
        for i in range(1, SCREEN_H+1, 2):
            v = 0  # Инициализация переменной для хранения значения символа Брайля

            # Сопоставление 4x2 пикселей одному символу Брайля
            for k in range(8):
                x = j  # Начальная координата x
                y = i  # Начальная координата y
                
                # Определение точных координат пикселя в зависимости от значения k
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

                # Если пиксель активен, устанавливаем соответствующий бит в переменной v
                if x < SCREEN_W and y < SCREEN_H and scr[x][y]:
                    v |= (1 << k)

            # Преобразование значения в символ Брайля
            braille_char = chr(0x2800 + v)
            line.append(braille_char)  # Добавляем символ в текущую строку

        output.append(''.join(line))  # Добавляем строку в общий список вывода

    print('\n'.join(output))  # Печать всех строк вывода






def print_screen_braille3(screen_bytes):
    SCREEN_H = 128  # Высота экрана в пикселях
    SCREEN_W = 64   # Ширина экрана в пикселях

    data = screen_bytes
    def get_bin(x): return format(x, 'b')  # Функция для преобразования числа в двоичное представление
    scr = numpy.zeros((SCREEN_W, SCREEN_H))  # Создаем пустую матрицу для хранения битов экрана

    x = y = 0  # Инициализация координат
    basex = 0  # Базовое значение для координаты x

    # Проход по каждому байту данных экрана
    for i in range(0, int(SCREEN_H * SCREEN_W / 8)):
        tmp = get_bin(data[i])  # Преобразование байта в двоичный формат
        tmp = '0' * (8 - len(tmp)) + tmp  # Дополнение строки нулями до 8 бит
        tmp = tmp[::-1]  # Зеркальное разворачивание строки (инверсия)

        x = basex  # Установка начальной позиции x
        y += 1  # Переход к следующей позиции y

        # Запись битов в матрицу scr
        for c in tmp:
            scr[x][y % SCREEN_H] = int(c)  # Записываем бит в матрицу scr
            x += 1  # Сдвигаем x вправо

        # Обновление базового значения x и сброс y после каждых 8 байтов
        if (i + 1) % SCREEN_H == 0:
            basex += 8
            y = 0

    output = []  # Список для хранения строк вывода

    # Проход по ширине экрана с шагом 4 пикселя
    for j in range(0, SCREEN_W, 4):
        line = []  # Список для хранения символов одной строки

        # Проход по высоте экрана с шагом 2 пикселя
        for i in range(1, SCREEN_H, 2):
            v = 0  # Инициализация переменной для хранения значения символа Брайля

            # Сопоставление 4x2 пикселей одному символу Брайля
            for k in range(8):
                x = j  # Начальная координата x
                y = i  # Начальная координата y
                
                # Определение точных координат пикселя в зависимости от значения k
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

                # Проверяем границы массива и устанавливаем соответствующий бит в переменной v
                if x < SCREEN_W and y < SCREEN_H and scr[x][y]:
                    v |= (1 << k)

            # Преобразование значения в символ Брайля
            braille_char = chr(0x2800 + v)
            line.append(braille_char)  # Добавляем символ в текущую строку

        output.append(''.join(line))  # Добавляем строку в общий список вывода

    print('\n'.join(output))  # Печать всех строк вывода


