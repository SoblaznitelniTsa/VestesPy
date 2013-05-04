# -*- coding: utf-8 -*-
import select as S
import threading

EMPTY = []
POLLING_TIMEOUT = 0.5

class select:
	def __init__(self, server):
		self._lock = threading.Lock()
		self.server = server
		self.connections = [server._socket]
		self.to_remove = []

	def remove(self, conn):
		if not conn:
			return
		with self._lock:
			try:
				self.to_remove.append(conn)
			except ValueError:
				pass

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
				read = S.select(self.connections, EMPTY, EMPTY, POLLING_TIMEOUT)[0]
			except Exception:
				continue

			self.update(read)

			if read:
				for sock in read:
					if sock == server._socket:
						conn, addr = server._socket.accept()
						with self._lock:
							self.connections.append(conn)
					else:
						server._handle_raw(sock)

class epoll:
	def __init__(self, server):
		self._lock = threading.Lock()
		self.server = server
		self.epoll = S.epoll()
		self.connections = {}
		self.to_remove = []

	def remove(self, conn):
		fileno = conn.fileno()
		try:
			self.epoll.unregister(fileno)
		except Exception:
			pass
		with self._lock:
			if fileno in self.connections:
				del self.connections[fileno]

	def serve(self):
		server = self.server
		socket = server._socket
		self.epoll.register(socket, S.EPOLLIN | S.EPOLLET)
		try:
			while True:
				events = self.epoll.poll(POLLING_TIMEOUT)
				for fileno, event in events:
					if fileno == socket.fileno():
						try:
							conn, addr = socket.accept()
							self.epoll.register(conn.fileno(), S.EPOLLIN | S.EPOLLET)
							with self._lock:
								self.connections[conn.fileno()] = conn
						except S.error:
							pass
					elif event & S.EPOLLIN:
						conn = self.connections.get(fileno, None)
						if conn:
							try:
								server._handle_raw(conn)
							except S.error:
								pass
					elif event & S.EPOLLHUP:
						conn = self.connections.get(fileno, None)
						if conn:
							self.remove(conn)
		finally:
			self.epoll.unregister(socket.fileno())
			self.epoll.close()