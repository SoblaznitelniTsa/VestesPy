# -*- coding: utf-8 -*-
import socket
import traceback
from vestespy import validators
from vestespy.tools import Headers, CRLF, HTTP_HEADER_END, HTTP_HEADER_SEPARATOR
from vestespy.response import Response
from vestespy.errors import HTTPError

def parse_headers(raw):
	data = raw.strip().split(CRLF)

	head = data.pop(0).split()

	method = validators.method(head[0])
	url = validators.url(head[1])
	query = url[1]
	url = url[0]
	protocol = validators.protocol(head[2])

	headers = Headers()
	for line in data:
		try:
			key, value = line.split(HTTP_HEADER_SEPARATOR)
		except Exception:
			continue

		headers[key.strip()] = value.strip()

	return headers, method, url, query, protocol

def finalize(req, res):
	try:
		req.trigger("end")
	except HTTPError as e:
		res.send_error(e.code, e.msg)
	except Exception:
		req.server.exception_handler()
		res.send_error(500)
		raise


def get_request_data(req):
	res = Response(req.connection, req.server, request=req)
	total = 0
	try:
		while True:
			res.check_self()

			if hasattr(req, "headers"):
				recv = req.server.HEADERS_LENGTH
			else:
				recv = req.server.CHUNK_LENGTH

			try:
				data = req.connection.recv(recv)
			except socket.error:
				break

			if not data:
				req._shutdown()
				return

			if not hasattr(req, "headers"):
				head, sep, chunk = data.partition(HTTP_HEADER_END)

				if sep != HTTP_HEADER_END:
					# headers are not inside initial data, kill it
					res.send_error(400)
					req._shutdown()
					return

				try:
					req.headers, req.method, req.url, req.query, req.protocol = parse_headers(head)
				except Exception:
					req.server.exception_handler()
					res.send_error(400)
					req._shutdown()
					return

				try:
					req.content_length = int(req.headers["content-length"])
				except (KeyError, TypeError, ValueError):
					req.content_length = 0

				try:
					req.server.trigger("request", [req, res])
				except HTTPError as e:
					res.send_error(e.status, e.msg)
					break
				except Exception:
					req.server.exception_handler()
					res.send_error(500)
					raise

				res.protocol = req.protocol

				data = chunk

			data_length = len(data)
			if data_length + total > req.content_length:
				data_length = req.content_length - total
				data = data[:data_length]

			total += data_length
			try:
				req.trigger("data", [data])
			except HTTPError as e:
				res.send_error(e.status, e.msg)
				break
			except Exception:
				req.server.exception_handler()
				res.send_error(500)
				raise

			if total == req.content_length:
				finalize(req, res)
				break

		if hasattr(req, "headers") and req.headers.get("connection", "") != "keep-alive":
			req._shutdown()
	finally:
		req._clean()
		del res.request, res.connection, res.server, res