# -*- coding: utf-8 -*-
import vestespy
import time

server = vestespy.Server(("localhost", 8080), debug=True)

dispatcher = vestespy.tools.Dispatcher()

HTML = b"""<!DOCTYPE html>
<html><head></head>
<body>
<form method="POST" enctype="multipart/form-data" action="/upload">
	<input type="file" name="data" multiple="multiple"><br/>
	<input type="submit" value="Submit"/>
</form>
</body></html>"""

def home(ev, req, res):
	res.headers["Content-Type"] = "text/html; charset=utf-8"
	res.send_all(HTML, buffer=False)

def ondata(ev, req, res, chunk):
	print(chunk)

def onend(ev, req, res):
	res.send_all("OK", buffer=False)

def upload(ev, req, res):
	req.on("data", ondata)
	req.on("end", onend)

dispatcher.register("/", home)
dispatcher.register("/upload", upload)

server.on("request", dispatcher.as_handler())

server.serve_forever()