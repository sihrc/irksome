"""
NIST Request Handler
"""
import json, traceback, logging

import tornado.web

from blank.routes import NISTError


LOGGER = logging.getLogger("")
class Handler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self, action):
        try:
            # Fetch appropriate handler
            if not hasattr(self, str(action)):
                raise NISTError("Sorry, %s route could not be found." % action, 404)

            # Pass along the data and get a result
            handler = getattr(self, str(action))
            handler(self.request.body)
        except NISTError as e:
            self.respond(e.message, e.status)
        except Exception as e:
            LOGGER.error(
                "\n\n======== NIST SERVER ERROR ========\n%s\n%s\n",
                 __file__,
                 traceback.format_exc()
            )
            error = NISTError("Oh madah fuck you, broke servah", 503)
            self.respond(error.message, error.status)


    def respond(self, data, code=200):
        self.set_status(code)
        self.write(json.dumps({
            "status": code,
            "data": data
        }))
        self.finish()
