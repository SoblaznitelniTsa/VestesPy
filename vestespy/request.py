# -*- coding: utf-8 -*-
import socket
from vestespy.tools import EventManager, Headers

class Request(EventManager):

	def __init__(self, conn, server):
		self.connection = conn
		self.connection.setblocking(0)
		self.server = server
		super().__init__()

	def shutdown(self):
		self.server.method.remove(self.connection)
		try:
			self.connection.shutdown(socket.SHUT_RDWR)
			self.close()
		except Exception:
			pass
		finally:
			del self.server, self.connection