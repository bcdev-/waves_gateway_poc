#!/usr/bin/env python3
import sys

if sys.version_info < (3,0):
    print("This program has to be run with Python 3 interpreter.")
    print("Try: python3 %s" % sys.argv[0])
    sys.exit(1)

from src.gateway import Gateway
if __name__ == "__main__":
    gateway = Gateway()
    gateway.start()

