# -*- coding: utf-8 -*-
EMPTY = b""

class HTTPError(Exception):
	def __init__(self, code, msg=None):
		self.code = code
		self.msg = msg or EMPTY