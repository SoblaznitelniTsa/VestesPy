VestesPy
===

Python3 Asynchronous Web Server and a lightweight framework.

-

**Prerequisites:**

NO DEPENDENCIES except for Python 3.x (tested with Python3.3).

**Example:**

VestesPy is very easy to use. All you need to do is create a subclass of `vesespy.Server` class:

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
      
    server = MyServer(("localhost", 8080))
    server.serve_forever()

**Documentation:**

-

**class vestespy.Server**
  - **init(self, addr, debug=False, select="select", handler=Request, max_workers=50)** Initializes an instance of the server. The server initializes a thread pool to handle incoming requests (with `max_workers` as number of threads). Currently supported select mechanisms are `select` and `epoll`. `handler` has to be a subclass of `Request`.
  - **serve_forever(self)** Fires the server.
  - **shutdown(self)** Kills the server.

In order to use the server you should implement the following methods (of which only `after_request` is mandatory):
  - **before_request(self, req)** Fires after receiveing headers, but before body is ready.
  - **stream_request(self, req, chunk)** Fires after receiveing chunks of data (by default they are buffered).
  - **after_request(self, req)** Fires after both headers and body is ready. This method has to return an instance of `Response` object.

Note that returning `False` in any of these methods will result in killing the connection.

-

**class vestespy.request.Request**
Passed to server's `before_request`, `stream_request` and `after_request`. Some of the interesting properties:

  - **headers** Dict of parsed heaedrs;
  - **method** One of the HTTP methods;
  - **url** without query string;
	- **query** parsed query string;
	- **protocol** probably `HTTP/1.1` nowadays;
  - **body** body of the request as a `bytes` instance;

-

**class vestespy.response.Response**
  - **init(self, body, mime=None, charset=None)** The `body` should be either `str` or `bytes`.

-

**class vestespy.response.ChunkResponse**
  - **init(self, stream, mime=None, charset=None)** The `stream` should be any iterable.

Note that `ChunkResponse` will set `Transfer-Encoding: chunked` header and will send each item in `stream` as a chunk (perfect if you don't know the length of `stream`).

-

**class vestespy.response.StreamResponse**
  - **init(self, stream, mime=None, charset=None, length=None)** The `body` should be either `str` or `bytes`.

This is similar to `ChunkResponse` except it requires `length` parameter (which is the length of entire data in `stream`, not number of chunks). It sets `Content-Length: length` header and does the normal streaming.
