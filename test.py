import vestespy

class MyServer(vestespy.Server):
	def before_request(self, req):
		print(req.url)
		super().before_request(req)

	def stream_request(self, req, chunk):
		super().stream_request(req, chunk)

	def after_request(self, req):
		res = vestespy.response.Response("Hello world!")
		res.headers["Cache-Control"] = "no-cache"
		return res

server = MyServer(("localhost", 8080), debug=True, select="epoll")
server.serve_forever()