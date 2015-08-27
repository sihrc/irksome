"""
NIST Request Handler
"""
from blank.routes.handler import Handler
from blank.routes import unpack, type_check

class NISTHandler(Handler):

    @unpack("query")
    @type_check(str)
    def search(self, query):
        self.respond("Your query was accepted. Please await results. Bitch.")


NistRoute = (r"/(?P<action>[a-zA-Z]+)?", NISTHandler)
