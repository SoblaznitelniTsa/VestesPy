# -*- coding: utf-8 -*-
import select as S
import threading

EMPTY = []

class select:
	def __init__(self, server):
		self._lock = threading.Lock()
		self.server = server
		self.connections = [server._socket]
		self.to_remove = []
		self.handlers = {}

	def remove(self, handler):
		if not handler or not hasattr(handler, "connection"):
			return
		with self._lock:
			try:
				self.to_remove.append(handler.connection)
			except ValueError:
				pass
			if handler.connection in self.handlers:
				del self.handlers[handler.connection]

	def update(self, lst=None):
		if self.to_remove:
			with self._lock:
				for sock in self.to_remove:
					if lst:
						try:
							lst.remove(sock)
						except ValueError:
							pass
					try:
						self.connections.remove(sock)
					except ValueError:
						pass
				self.to_remove = []
	
	def serve(self):
		server = self.server
		while True:
			self.update()

			try:
				read = S.select(self.connections, EMPTY, EMPTY, 0.5)[0]
			except Exception:
				continue

			self.update(read)

			if read:
				for sock in read:
					if sock == server._socket:
						conn, addr = server._socket.accept()
						handler = server.handler_class(conn, addr, server)
						with self._lock:
							self.handlers[conn] = handler
							self.connections.append(conn)
					else:
						handler = self.handlers.get(sock, None)
						if not handler:
							try:
								with self._lock:
									self.to_remove.append(sock)
							except ValueError:
								pass
						else:
							server._handle_raw(handler)