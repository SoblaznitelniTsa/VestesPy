# -*- coding: utf-8 -*-
from urllib.parse import parse_qs

METHODS = set([ b"get", b"post", b"head", b"put", b"delete", b"trace", b"options", b"connect", b"patch" ])
def method(data):
	data = data.strip().lower()
	if data in METHODS:
		return data.upper()
	raise ValueError()

def url(data):
	url, part, qs = data.strip().partition(b"?")
	return url.decode("utf-8"), parse_qs(qs.decode("utf-8"), keep_blank_values=True)

def protocol(data):
	data = data.strip()
	return data

def valid_http_header(key, value):
	if key == "content-length":
		return int(value)
	return value