# -*- coding: utf-8 -*-
import traceback
from vestespy import validators
from vestespy.dispatcher import Dispatcher

CRLF = b"\r\n"
HTTP_HEADER_END = b"\r\n\r\n"
HTTP_HEADER_SEPARATOR = b":"

def dummy(*args, **kwargs):
	pass

def generate_simple_http(content):
	if not isinstance(content, bytes):
		content = bytes(content, "utf-8")
	result = b"<!DOCTYPE html><html><head></head><body>" + content + b"</body></html>"
	return result

class Headers:
	def __init__(self):
		self._data = {}

	def get(self, key, *args, **kwargs):
		try:
			return self._data[key][0]
		except KeyError:
			if args:
				return args[0]
			if "default" in kwargs:
				return kwargs["default"]
			raise

	def __getitem__(self, key):
		if not isinstance(key, str):
			raise KeyError(key)
		key = key.lower()
		return self._data[key][0]

	def __contains__(self, key):
		return key in self._data

	def __setitem__(self, key, value):
		if isinstance(key, bytes):
			key = key.decode("utf-8")
		if not isinstance(key, str):
			raise KeyError(key)
		if isinstance(value, bytes):
			value = value.decode("utf-8")
		if isinstance(value, str):
			value = value.strip()

		key = key.strip()
		newkey = key.lower()
		self._data[newkey] = (value, key)

	def __delitem__(self, key):
		if key in self._data:
			del self._data[key]

	def __iter__(self):
		return self._data.keys()

	def items(self):
		return self._data.items()
	def values(self):
		return self._data.values()

	def __repr__(self):
		log = ["HEADERS:"]
		for key, value in self._data.items():
			log.append(key + ": " + str(value[0]))
		return "\n ".join(log)

	def validate(self):
		keys = list(self._data.keys())
		for key in keys:
			try:
				org = self._data[key]
				value = validators.valid_http_header(key, org[0])
				self._data[key] = (value, org[1])
			except Exception:
				del self._data[key]

def default_exception_handler():
	traceback.print_exc()

class EventManager:
	def __init__(self, *args, **kwargs):
		self._events = {}
		self.exception_handler = default_exception_handler

	def set_exception_handler(self, handler):
		self.exception_handler = handler

	def on(self, name, handler):
		if not callable(handler):
			raise TypeError("You have to pass callables to .on method!")
		if name not in self._events:
			self._events[name] = []
		self._events[name].append(handler)

	def off(self, name, handler=None):
		if name not in self._events:
			return

		if handler is not None:
			try:
				self._events[name].remove(handler)
			except ValueError:
				pass
		else:
			self._events[name] = None

		if not self._events[name]:
			del self._events[name]

	def trigger(self, name, args=[]):
		if name not in self._events:
			return

		for handler in self._events[name]:
			try:
				handler(self, *args)
			except Exception:
				self.exception_handler()