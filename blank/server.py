import tornado.ioloop
import tornado.web

from blank.routes.nist import NistRoute

def main(debug = True, port = 3000):
    application = tornado.web.Application([
        NistRoute
    ], debug = debug
     , autoreload = debug)

    application.listen(port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
