import sys
import time

if sys.platform != "win32":
    import fcntl
    import termios
    import os

    class NonBlockingInput(object):
        def __enter__(self):
            # canonical mode, no echo
            self.old = termios.tcgetattr(sys.stdin)
            new = termios.tcgetattr(sys.stdin)
            new[3] = new[3] & ~(termios.ICANON | termios.ECHO)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new)

            # set for non-blocking io
            self.orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
            fcntl.fcntl(sys.stdin, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
            return self

        def __exit__(self, *args):
            # restore terminal to previous state
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old)

            # restore original
            fcntl.fcntl(sys.stdin, fcntl.F_SETFL, self.orig_fl)

        def get_data(self):
            try:
                return sys.stdin.read(1)
            except IOError:
                return None
else:
    import msvcrt

    class NonBlockingInput(object):
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get_data(self):
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8')
            return None

# Usage:
#
# with NonBlockingInput() as nbi:
#     while True:
#         c = nbi.get_data()
#         if c:
#             print('tick', repr(c))
#         time.sleep(0.1)