# -*- coding: utf-8 -*-
import re

HTML404 = b"<!DOCTYPE html><html><head></head><body>404 Page Not Found</body></html>"
def handle404(server, req, res):
	res.send_error(404, HTML404)

REGEXP = re.compile(r":(\w+)")
GROUP_REGEXP = re.compile(r"P<(.*)>")

class Dispatcher:

	def __init__(self, *args, **kwargs):
		self.patterns = []
	
	def register(self, pattern, handler, name=None):
		if not callable(handler):
			raise TypeError("You can only register callables!")

		groups = REGEXP.findall(pattern)
		for group in groups:
			pattern = re.sub(r":\w+", "(?P<"+group+">[0-9A-Za-z]*?)", pattern, count=1)

		groups = GROUP_REGEXP.findall(pattern)

		pattern += "$"

		pattern = re.compile(pattern)

		self.patterns.append((pattern, groups, handler, name))

	def get_pattern(self, url=None, name=None):
		if url is not None and name is not None:
			raise ValueError("You cannot pass both url and name to get_pattern!")

		if url is not None:
			for pattern in self.patterns:
				reg = pattern[0]
				if reg.match(url):
					return pattern
		elif name is not None:
			for pattern in self.patterns:
				if pattern[3] == name:
					return pattern

		return (None, None, handle404, None)

	def as_handler(self):
		def handler(server, req, res):
			pattern = self.get_pattern(req.url)

			if pattern[0] is None:
				pattern[2](server, req, res)
			else:
				reg = pattern[0]
				match = reg.match(req.url)
				kwargs = {}
				for group in pattern[1]:
					kwargs[group] = match.group(group)
				pattern[2](server, req, res, **kwargs)
		return handler