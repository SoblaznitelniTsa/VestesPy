# -*- coding: utf-8 -*-
import socket
import traceback
from vestespy import validators
from vestespy.tools import Headers, CRLF, HTTP_HEADER_END, HTTP_HEADER_SEPARATOR
from vestespy.response import Response

HEADERS_LENGTH = 8192
STREAM_LENGTH = 16384

def parse_headers(raw):
	data = raw.strip().split(CRLF)

	head = data.pop(0).split()

	method = validators.method(head[0])
	url = validators.url(head[1])
	protocol = validators.protocol(head[2])

	headers = Headers()
	for line in data:
		try:
			key, value = line.split(HTTP_HEADER_SEPARATOR)
		except Exception:
			continue

		headers[key.strip()] = value.strip()

	return headers, method, url, protocol

def get_request_data(req):
	res = Response(req.connection, req.server)
	total = 0
	while True:
		if hasattr(req, "headers"):
			recv = STREAM_LENGTH
		else:
			recv = HEADERS_LENGTH

		try:
			data = req.connection.recv(recv)
		except socket.error:
			return

		if not data:
			req.shutdown()
			return

		if not hasattr(req, "headers"):
			head, sep, chunk = data.partition(HTTP_HEADER_END)

			if sep != HTTP_HEADER_END:
				# headers are not inside initial data, kill it
				req.shutdown()
				return

			try:
				req.headers, req.method, req.url, req.protocol = parse_headers(head)
			except Exception:
				traceback.print_exc()
				raise

			try:
				req.content_length = req.headers["content-length"]
			except KeyError:
				# TODO: return HTTP error?
				req.content_length = 0

			req.server.trigger("request", [req, res])

			res.protocol = req.protocol

			data = chunk

		data_length = len(data)
		if data_length + total > req.content_length:
			data_length = req.content_length - total
			data = data[:data_length]

		total += data_length
		req.trigger("data", [res, data])

		if total == req.content_length:
			req.trigger("end", [res])
			if req.headers.get("connection", "") != "keep-alive":
				req.shutdown()
			return