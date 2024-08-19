import fcntl
import termios
import sys
import os
import time

# https://gist.github.com/ali1234/7a6899ecc77a67a643de65a919457020


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

    def __exit__(self, *args):
        # restore terminal to previous state
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old)

        # restore original
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, self.orig_fl)


# Usage:
#
# with NonBlockingInput():
#     while True:
#         c = sys.stdin.read(1)
#         print('tick', repr(c))
#         time.sleep(0.1)
