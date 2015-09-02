import argparse

import tornado.ioloop
import tornado.web

from blank.routes.nist import NistRoute

def main(port, debug = True):
    application = tornado.web.Application([
        NistRoute
    ], debug = debug
     , autoreload = debug)

    application.listen(port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, help="port to run app on", default=3000)
    parsed = parser.parse_args()
    main(port = parsed.port)
