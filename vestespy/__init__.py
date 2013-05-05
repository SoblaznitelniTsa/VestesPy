# -*- coding: utf-8 -*-
__version_info__ = (0, 1)
__version__ = ".".join( str(v) for v in __version_info__ )

import sys
if sys.version_info[0] < 3:
	raise Exception("You need Python3+ to use VestesPy.")

from vestespy.server import Server
from vestespy.request import Request
from vestespy.response import Response
from vestespy.errors import HTTPError
from vestespy import tools