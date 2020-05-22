# !/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if len(sys.argv) < 2:
    print("Please enter the file name.")
    sys.exit()

cpu = CPU()
cpu.load(sys.argv[1])
cpu.run()

