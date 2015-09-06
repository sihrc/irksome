#!/usr/bin/python
#By Steve Hanov, 2011. Released to the public domain
import os
from blank.data_utils import load, OUTPUT_DIR, cache, SYMBOL_MAPPING
from fuzzywuzzy import fuzz


# The Trie data structure keeps a set of words, organized with one node for
# each letter. Each node has a branch for each letter that may follow it in the
# set of words.
class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}

    def insert( self, word ):
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()

            node = node.children[letter]

        node.word = word

def create_trie():
    dictionary = load(os.path.join(OUTPUT_DIR, "element_data.p"))
    # read dictionary file into a trie
    trie = TrieNode()
    words = []
    for key in dictionary:
        words += key.split(" ")
    for key in set(words):
        trie.insert(key)
    for key in SYMBOL_MAPPING.keys():
        trie.insert(key)

    cache(trie, os.path.join(OUTPUT_DIR, "trie.p"))

# The search function returns a list of all words that are less than the given
# maximum distance from the target word
def search( word ):
    maxCost = int(len(word) * .6)
    # build first row
    currentRow = range( len(word) + 1 )
    results = {}

    # recursively search each branch of the trie
    for letter in trie.children:
        searchRecursive( trie.children[letter], letter, word, currentRow,
            results, maxCost )

    if not results.keys():
        return None

    results = results[min(results.keys())]
    if len(results) > 1:
        best = 0
        for result in results:
            ratio = fuzz.partial_ratio(word, result)
            if ratio > best:
                best_result = result
                best = ratio
    else:
        best_result = results[0]
    return best_result


# This recursive helper is used by the search function above. It assumes that
# the previousRow has been filled in already.
def searchRecursive( node, letter, word, previousRow, results, maxCost ):
    columns = len( word ) + 1
    currentRow = [ previousRow[0] + 1 ]

    # Build one row for the letter, with a column for each letter in the target
    # word, plus one for the empty string at column 0
    for column in xrange( 1, columns ):
        insertCost = currentRow[column - 1] + 1
        deleteCost = previousRow[column] + 1

        if word[column - 1] != letter:
            replaceCost = previousRow[ column - 1 ] + 1
        else:
            replaceCost = previousRow[ column - 1 ]

        currentRow.append( min( insertCost, deleteCost, replaceCost ) )

    # if the last entry in the row indicates the optimal cost is less than the
    # maximum cost, and there is a word in this trie node, then add it.
    if currentRow[-1] <= maxCost and node.word != None:
        results[currentRow[-1]] = results.get(currentRow[-1], []) + [node.word]

    # if any entries in the row are less than the maximum cost, then
    # recursively search each branch of the trie
    if min( currentRow ) <= maxCost:
        for letter in node.children:
            searchRecursive( node.children[letter], letter, word, currentRow,
                results, maxCost )

create_trie()
trie = load(os.path.join(OUTPUT_DIR, "trie.p"))
