VestesPy
===

Python3 Asynchronous Web Server and a lightweight framework.

-

**Prerequisites:**

NO DEPENDENCIES except for Python 3.x (tested with Python3.3).

**Example:**

VestesPy is very easy to use. All you need to do is create an instance of `vesespy.Server` class:

    import vestespy

    def onend(ev, req, res):
      res.send_all("TEST")

    def onrequest(ev, req, res):
      req.on("end", onend)

    server = vestespy.Server(("localhost", 8080))
    server.on("request", onrequest)

    server.serve_forever()

**Documentation:**

-

**class vestespy.Server**
  - **init(self, addr, debug=False, select="select", handler=Request, max_workers=50)** Initializes an instance of the server. The server initializes a thread pool to handle incoming requests (with `max_workers` as number of threads). Currently supported select mechanisms are `select` and `epoll`. `handler` has to be a subclass of `Request`.
  - **serve_forever(self)** Fires the server.
  - **shutdown(self)** Kills the server.

The server is also an event emitter. It responds to the following events:
  - **request** handler is a function of the form **def onrequest(server, req, res)**. This event fires once the request is accepted and headers are parsed.

-

**class vestespy.Request**
Passed to server's `request` handler. It's an object associated to the request. It is an event emitter with the following events:

  - **data** Fires when data arrives; Note that a developer has to take care of combining/parsing chunked body; At the moment the request has to have `Content-Length` header, otherwise VestesPy will treat it as a request without body; The handler for this event is of type **def ondata(ev, req, res, chunk)**.
  - **end** Fires at the end of the request; The handler for this event is of type **def onend(ev, req, res)**;

-

**class vestespy.Response**
A response object with the following methods:
  - **send_all(data)** Sends `data` as a one big response. `data` has to be either `str` or `bytes`. It sets `Content-Length` header as well.
  - **send_stream(stream, length)** Sends stream of `str` or `bytes` as a response. The total amount of data must be equal to `length` (thus it has to be preevaluated earlier).
  - **send_chunked(stream)** As above, except it does not require length. It sends the data as a chunked data (thus it sets `Transfer-Enocoding: chunked` header).

-

**class vestespy.tools.Dispatcher**

Creates a route dispatcher. The usage is very simple:

    import vestespy

    server = vestespy.Server(("localhost", 8080), debug=True)

    dispatcher = vestespy.tools.Dispatcher()

    def home(ev, req, res):
      res.send_all("test")
    dispatcher.register("/", home)

    def test(ev, req, res, id=None):
      res.send_all("ID: %s" % id)
    dispatcher.register("/test/:id", test)

    server.on("request", dispatcher.as_handler())

    server.serve_forever()

You may pass a regular expression to `register` as well.

**LICENSE**

<rafael.szefler@gmail.com> wrote this code. As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return.

Rafael Szefler