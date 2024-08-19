#!/usr/bin/env python3
#!/usr/bin/env python3

import sys
import serial

from flipperzero_protobuf_py.flipper_protobuf import ProtoFlipper
from src.cli_helpers import print_hex

from src.helpers import print_screen_braille3 as print_screen_braille, print_lines_in_one_place, flipper_serial_by_name
import time

from src.non_blocking_input import NonBlockingInput

def main():
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " <name or serial port>")
        sys.exit(1)

    flp_serial = flipper_serial_by_name(sys.argv[1])
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

    proto = ProtoFlipper(flipper)

    cntr = 0
    scr_data_str_old = None

    menuitems = "Controls: w,a,s,d - arrows short, W,A,S,D - arrows long, SPACE - OK, b - BACK, q - quit"

    # Reserve space for screen
    print(menuitems)
    print("\n" * int(64/4-1))

    while True:
        key = None
        with NonBlockingInput():
            key = sys.stdin.read(1)
        
        scrbytes = proto.cmd_gui_snapshot_screen()
        scr_data_str = print_screen_braille(scrbytes, True)

        if scr_data_str != scr_data_str_old or key != '':
            print_lines_in_one_place(scr_data_str.split('\n'))

            if key != '':
                # print('tick', repr(key), print_hex(key.encode('utf-8')))
                if key == 'q':
                    break
                elif key == 'w' or key == '\x1b[A':
                    proto.cmd_gui_send_input("SHORT UP")
                elif key == 's' or key == '\x1b[B':
                    proto.cmd_gui_send_input("SHORT DOWN")
                elif key == 'a' or key == '\x1b[D':
                    proto.cmd_gui_send_input("SHORT LEFT")
                elif key == 'd' or key == '\x1b[C':
                    proto.cmd_gui_send_input("SHORT RIGHT")
                elif key == ' ':
                    proto.cmd_gui_send_input("SHORT OK")
                elif key == 'b':
                    proto.cmd_gui_send_input("SHORT BACK")
                elif key == 'W':
                    proto.cmd_gui_send_input("LONG UP")
                elif key == 'S':
                    proto.cmd_gui_send_input("LONG DOWN")
                elif key == 'A':
                    proto.cmd_gui_send_input("LONG LEFT")
                elif key == 'D':
                    proto.cmd_gui_send_input("LONG RIGHT")
            
            key = ''

            scr_data_str_old = scr_data_str
    
        time.sleep(0.01)
        
        cntr += 1


if __name__ == '__main__':
    main()