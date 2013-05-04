import vestespy

def onend(req, res):
	res.send_all("TEST")

def onrequest(server, req, res):
	req.on("end", onend)

server = vestespy.Server(("localhost", 8080))
server.on("request", onrequest)

server.serve_forever()