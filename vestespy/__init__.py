# -*- coding: utf-8 -*-
import sys
if sys.version_info[0] < 3:
	raise Exception("You need Python3+ to use VestesPy.")

from vestespy.server import Server
from vestespy.request import Request
from vestespy.response import Response

__version__ = (0, 1)