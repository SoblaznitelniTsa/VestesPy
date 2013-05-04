# -*- coding: utf-8 -*-
import socket
import traceback
from vestespy import selects
from concurrent.futures import ThreadPoolExecutor
from vestespy.request import Request
from vestespy.tools import EventManager
from vestespy.parser import get_request_data

class Server(EventManager):
	def __init__(self, addr, handler=Request, select="select", max_workers=50, debug=False):
		if not issubclass(handler, Request):
			raise ValueError("Server instance only accepts subclasses of Request as handlers!")
		self._pool = ThreadPoolExecutor(max_workers=max_workers)
		self.address = addr
		self.handler_class = handler
		
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind(addr)
		self._socket.setblocking(0)
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._socket.listen(50)

		self.method = getattr(selects, select)(self)
		self.debug = debug
		super().__init__()

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

	def serve_forever(self):
		try:
			self.method.serve()
		finally:
			self.shutdown()

	def handle_raw(self, conn):
		req = self.handler_class(conn, self)
		try:
			get_request_data(req)
		except Exception:
			traceback.print_exc()
			raise

	def _handle_raw(self, conn):
		self._pool.submit(self.handle_raw, conn)