import os
import sys

from ..core import argv_parse


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


if __name__ == "__main__":
    argv_parse.ArgvParse()
