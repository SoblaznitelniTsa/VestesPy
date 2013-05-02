# -*- coding: utf-8 -*-
import socket
import traceback
from vestespy import validators
from concurrent.futures import ThreadPoolExecutor
from vestespy.tools import Headers
from vestespy.response import Response

HTTP_HEADER_SEPARATOR = b"\r\n\r\n"

class Request:
	def __init__(self, conn, addr, server):
		self.connection = conn
		self.address = addr
		self.server = server
		self._buffer = b""
		self.alive = True

	def _parse_headers(self):
		lines = self._headers.split(b"\r\n")
		head = lines.pop(0).split()

		self.method = validators.method(head[0])
		self.url, self.query = validators.url(head[1])
		self.protocol = validators.protocol(head[2])

		self.headers = Headers()
		for line in lines:
			line = line.split(b":")
			if len(line) == 2:
				self.headers[line[0]] = line[1]

		self.headers.validate()

	def shutdown(self):
		self.alive = False
		try:
			self.connection.shutdown(socket.SHUT_WR)
			self.connection.close()
		except Exception:
			pass
		try:
			self.server.method.remove(self)
		finally:
			if hasattr(self, "_buffer"):
				del self._buffer
			del self.server, self.connection

	def _handle_buffer(self, chunk):
		expected_length = self.headers.get("content-length", 0)

		if isinstance(chunk, bytes):
			chunk_length = len(chunk)
			if chunk_length + self._length > expected_length:
				chunk_length = expected_length - self._length
				chunk = chunk[:chunk_length]
			self._length += chunk_length
			response = None

			try:
				result = self.server.stream_request(self, chunk)
			except Exception:
				traceback.print_exc()
				self.shutdown()
				return

			if result == False:
				self.shutdown()
				return

			if self._length == expected_length:
				try:
					response = self.server._after_request(self)
				except Exception:
					traceback.print_exc()
					self.shutdown()
					return
				self._length = 0

			if response == False:
				self.shutdown()
				return

			if response is not None:
				if not isinstance(response, Response):
					self.shutdown()
					return
				response.protocol = self.protocol
				try:
					response.send(self)
				finally:
					del response
					if hasattr(self, "_headers"):
						del self._headers
					if self.headers.get("connection", "") != "keep-alive":
						self.shutdown()

	def _handle_chunked(self, data):
		raise NotImplemented()

	def _handle_raw(self):
		if not self.alive:
			self.shutdown()
			return

		data = self.connection.recv(32768)
		if data:
			if not hasattr(self, "_headers"):
				headers, part, rest = data.partition(HTTP_HEADER_SEPARATOR)
				if part != HTTP_HEADER_SEPARATOR:
					# we don't allow headers to be too long
					self.shutdown()
					return
				self._headers = headers
				data = rest
				self._length = 0
				try:
					self._parse_headers()
				except Exception:
					self.shutdown()
					return
				self._headers = True

				try:
					result = self.server.before_request(self)
				except Exception:
					traceback.print_exc()
					raise

				if result == False:
					self.shutdown()
					return

			if False:
				self._handle_chunked(data)
			else:
				self._handle_buffer(data)

		else:
			self.shutdown()