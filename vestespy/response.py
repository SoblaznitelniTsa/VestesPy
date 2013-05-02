# -*- coding: utf-8 -*-
from vestespy.tools import Headers, generate_simple_http
import traceback
from vestespy import http_status

CRLF = b"\r\n"

class Response:
	def __init__(self, body, mime=None, charset=None):
		self.body = body
		self.headers = Headers()
		self.status = 200
		self.combined = False

		if not charset:
			charset = "utf-8"
		self.charset = charset
		if not mime:
			mime = "text/html; charset="+charset
		self.headers["Content-Type"] = mime

	def postprocessing(self):
		if self.body is not None:
			if not isinstance(self.body, bytes):
				self.body = bytes(self.body, self.charset)
			self.headers["Content-Length"] = len(self.body)

	def combine(self):
		if self.combined:
			return
		self.combined = True
		self.postprocessing()

		if not hasattr(self, "protocol"):
			self.protocol = b"HTTP/1.1"

		if self.status not in http_status.name:
			self.status = 500

		status = str(self.status) + " " + http_status.name[self.status]
		status = bytes(status, self.charset)

		response = [self.protocol + b" " + status]
		for value in self.headers.values():
			response.append(bytes(str(value[1]), self.charset)+b":"+bytes(str(value[0]), self.charset))
		response.append(CRLF)
		response = CRLF.join(response)
		self.binary_headers = response

	def send_headers(self, req):
		try:
			req.connection.sendall(self.binary_headers)
		except Exception:
			pass			

	def send(self, req):
		if not hasattr(self, "protocol") and hasattr(req, "protocol"):
			self.protocol = req.protocol
		self.combine()
		self.send_headers(req)
		if isinstance(self.body, bytes):
			try:
				req.connection.sendall(self.body)
			except Exception:
				return

class HTTPError(Response):
	def __init__(self, code, body=None, debug=False):
		if code not in http_status.description:
			code = 500
		if body is None:
			body = "<div><b>" + str(code) + " " + http_status.name[code] + "</b></div>"
			body += "<div>" + http_status.description[code] + "</div>"
		if not isinstance(body, bytes):
			body = bytes(body, "utf-8")
		html = b"<!DOCTYPE html><html><head><body>" + body
		if code == 500 and debug:
			try:
				back = traceback.format_exc()
			except AttributeError:
				back = "UNKNOWN TRACEBACK"
			back = bytes(back, "utf-8")
			html += b"<div><pre>"+back+b"</pre></div>"
		html += b"</body></html>"
		super().__init__(html)
		self.status = code

class StreamResponse(Response):
	def __init__(self, stream, mime=None, charset=None, length=None):
		super().__init__(None, mime, charset)
		self.length = int(length)
		self.stream = stream

	def send(self, req):
		self.headers["Content-Length"] = self.length
		self.combine()
		self.send_headers(req)

		counter = 0
		for data in self.stream:
			if isinstance(data, str):
				data = bytes(data, self.charset)
			if not isinstance(data, bytes):
				raise TypeError("StreamResponse can only send stream of strings or bytes!")
			data_length = len(data)
			if counter + data_length > self.length:
				data_length = self.length - counter
				data = data[:data_length]
			try:
				req.connection.sendall(data)
			except Exception:
				pass
			counter += data_length
			if counter == self.length:
				break

class ChunkedResponse(Response):
	def __init__(self, stream, mime=None, charset=None):
		super().__init__(None, mime, charset)
		self.stream = stream

	def send(self, req):
		self.headers["Transfer-Encoding"] = "chunked"
		self.combine()
		self.send_headers(req)
		for data in self.stream:
			if isinstance(data, str):
				data = bytes(data, self.charset)
			if not isinstance(data, bytes):
				raise TypeError("ChunkedResponse can only send stream of strings or bytes!")
			data_length = bytes("%X" % len(data), "ascii")
			data = data_length + CRLF + data + CRLF
			try:
				req.connection.sendall(data)
			except Exception:
				pass
		try:
			req.connection.sendall(b"0"+CRLF+CRLF)
		except Exception:
			pass