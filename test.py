# -*- coding: utf-8 -*-
import vestespy
import time

server = vestespy.Server(("localhost", 8080), debug=True)

dispatcher = vestespy.tools.Dispatcher()

def test(server, req, res):
	res.send_all("test")

def test2(server, req, res, id=None):
	res.send_all("ID: %s" % id)

dispatcher.register("/", test)
dispatcher.register("/test/:id", test2)

server.on("request", dispatcher.as_handler())

server.serve_forever()