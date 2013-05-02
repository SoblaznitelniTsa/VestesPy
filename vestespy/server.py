# -*- coding: utf-8 -*-
import socket
from vestespy import selects
import traceback
from concurrent.futures import ThreadPoolExecutor
from vestespy.request import Request
from vestespy.response import HTTPError

class Server:
	def __init__(self, addr, handler=Request, select="select", max_workers=50, debug=False):
		if not issubclass(handler, Request):
			raise ValueError("Server instance only accepts subclasses of Request as handlers!")
		self._pool = ThreadPoolExecutor(max_workers=max_workers)
		self.address = addr
		self.handler_class = handler
		
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind(addr)
		self._socket.settimeout(0)
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._socket.listen(5)

		self.method = getattr(selects, select)(self)
		self.debug = debug

	def shutdown(self):
		try:
			self._pool.shutdown(wait=True)
		except Exception:
			pass
		try:
			self._socket.shutdown(socket.SHUT_WR)
			self._socket.close()
		except Exception:
			pass

	def before_request(self, req):
		pass

	def stream_request(self, req, chunk):
		req._buffer += chunk

	def _after_request(self, req):
		req.body = req._buffer
		req._buffer = b""
		try:
			return self.after_request(req)
		except Exception:
			traceback.print_exc()
			error = HTTPError(500, debug=self.debug)
			error.send(req)
			raise

	def serve_forever(self):
		try:
			self.method.serve()
		finally:
			self.shutdown()

	def _handle_raw(self, handler):
		self._pool.submit(handler._handle_raw)