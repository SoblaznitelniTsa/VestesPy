# -*- coding: utf-8 -*-
from vestespy import http_status
from vestespy.tools import Headers, CRLF

class Response:
	def __init__(self, conn, server):
		self.connection = conn
		self.server = server
		self.headers = Headers()
		self.status = 200
		self.protocol = b"HTTP/1.1"
		self.charset = "utf-8"

	def combine_headers(self):
		if not hasattr(self, "_cached_headers"):
			if self.status not in http_status.name:
				self.status = 500

			status = str(self.status) + " " + http_status.name[self.status]
			status = status.encode(self.charset)

			response = [self.protocol + b" " + status]
			for value in self.headers.values():
				key = str(value[1]).encode(self.charset)
				val = str(value[0]).encode(self.charset)
				response.append(key+b":"+val)
			response.append(CRLF)
			response = CRLF.join(response)
			self._cached_headers = response
		return self._cached_headers

	def send_all(self, data):
		if isinstance(data, str):
			data = data.encode(self.charset)
		if not isinstance(data, bytes):
			raise Exception("res.send_all accepts only str or bytes!")
		self.headers["Content-Length"] = len(data)

		headers = self.combine_headers()

		self.send(headers + data)

	def send_stream(self, iterable, total):
		total = int(total)
		self.headers["Content-Length"] = total

		headers = self.combine_headers()
		self.send(headers)

		current = 0
		for data in iterable:
			if isinstance(data, str):
				data = data.encode(self.charset)
			if not isinstance(data, bytes):
				raise Exception("res.send_stream accepts only a stream of str or bytes!")

			data_length = len(data)
			if current + len(data) > total:
				data_length = total - current
				data = data[:data_length]

			self.send(data)

			current += data_length
			if current == total:
				break

	def send_chunked(self, iterable):
		self.headers["Transfer-Encoding"] = "chunked"
		headers = self.combine_headers()
		self.send(headers)

		for data in iterable:
			if isinstance(data, str):
				data = data.encode(self.charset)
			if not isinstance(data, bytes):
				raise Exception("res.send_stream accepts only a stream of str or bytes!")

			data_length = ("%X" % len(data)).encode("ascii")
			data = data_length + CRLF + data + CRLF
			self.send(data)

		self.send(b"0"+CRLF+CRLF)

	def send(self, data):
		try:
			self.connection.sendall(data)
		except Exception:
			pass