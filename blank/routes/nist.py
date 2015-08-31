"""
NIST Request Handler
"""
import re

import indicoio

from blank.routes.handler import Handler
from blank.routes import unpack, type_check
from blank.data_utils import data, SYMBOL_MAPPING
from blank.data_utils.trie import search as spelling
from fuzzywuzzy import fuzz

KEYWORDS = data.ELEMENT_DATA.keys()


def filter_numbers(text):
    return re.sub("[^(0-9)^ ]", "", text)

class NISTHandler(Handler):
    @unpack("query")
    @type_check(str)
    def search(self, query):
        numbers = filter_numbers(query.lower())
        keywords = [numbers] + [
            SYMBOL_MAPPING.get(key, key)
                for key in indicoio.keywords(" ".join(map(spelling, query.lower().split(" "))), top_n=100).keys()
        ]
        keywords = " ".join(keywords)
        best = 0
        results = []
        for key in KEYWORDS:
            # ratio = fuzz.token_set_ratio(keywords, key)
            ratio = 0
            for word in keywords.split(" "):
                keys = key.split(" ")
                if word in keys:
                    ratio += 1

            if ratio > best:
                best = ratio
                results = []
                results.append((ratio, key, data.ELEMENT_DATA[key]))
            elif ratio == best:
                results.append((ratio, key, data.ELEMENT_DATA[key]))

        if len(results) > 3:
            for i in xrange(len(results)):
                results[i] = fuzz.ratio(keywords, results[i][1]), results[i][1], results[i][2]
        self.respond(sorted(results, reverse=True)[:5])

NistRoute = (r"/(?P<action>[a-zA-Z]+)?", NISTHandler)
