# -*- coding: utf-8 -*-
import socket
from vestespy.tools import EventManager

class Request(EventManager):

	def __init__(self, conn, server):
		self.connection = conn
		self.server = server
		super().__init__()

	def _clean_attr(self, attr):
		if hasattr(self, attr):
			delattr(self, attr)

	def _clean(self):
		self._clean_attr("server")
		self._clean_attr("connection")
		self._clean_attr("_events")
		self._clean_attr("excepttion_handler")

	def _shutdown(self):
		self.server.method.remove(self.connection)
		try:
			self.connection.shutdown(socket.SHUT_RDWR)
			self.close()
		except Exception:
			pass
		finally:
			self._clean()