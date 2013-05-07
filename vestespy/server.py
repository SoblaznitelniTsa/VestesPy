# -*- coding: utf-8 -*-
import socket
import traceback
import time
import sys
from vestespy import selects
from concurrent.futures import ThreadPoolExecutor
from vestespy.request import Request
from vestespy.tools import EventManager, dummy
from vestespy.parser import get_request_data
from vestespy.logger import Console

SOCKET_TRIES = 10

class Server(EventManager):
	def __init__(self, addr, handler=Request, 
			select="select", max_workers=50, debug=False,
			HEADERS_LENGTH=8192, CHUNK_LENGTH=16384):
		if not issubclass(handler, Request):
			raise ValueError("Server instance only accepts subclasses of Request as handlers!")
		self.console = Console()
		self._pool = ThreadPoolExecutor(max_workers=max_workers)
		self.handler_class = handler
		
		if isinstance(addr, tuple):
			self.address = addr
			self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			counter = 0
			self.console.info("Initializing VestesPy server", end="")
			while True:
				try:
					self.console.log(".", end="")
					self._socket.bind(addr)
				except Exception:
					counter += 1
					if counter >= SOCKET_TRIES:
						raise
					time.sleep(1)
				else:
					self.console.log(" Done!")
					break
			self._socket.setblocking(0)
			self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self._socket.listen(50)
		elif isinstance(addr, socket.socket):
			self._socket = addr
			self.address = addr.getsockname()
		else:
			raise TypeError("You have to pass either address tuple of instance of socket.socket to Server!")

		self.HEADERS_LENGTH = HEADERS_LENGTH
		self.CHUNK_LENGTH = CHUNK_LENGTH

		self.method = getattr(selects, select)(self)
		self.debug = debug
		if not debug:
			self.set_exception_handler(dummy)
		else:
			def exc():
				self.console.error("\n"+traceback.format_exc())
			self.set_exception_handler(exc)
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
		except KeyboardInterrupt:
			self.console.warn("Shutting down the server.")
		finally:
			self.shutdown()

	def handle_raw(self, conn):
		req = self.handler_class(conn, self)
		if not self.debug:
			req.set_exception_handler(dummy)
		
		try:
			get_request_data(req)
		except Exception:
			traceback.print_exc()
			raise

	def _handle_raw(self, conn):
		self._pool.submit(self.handle_raw, conn)