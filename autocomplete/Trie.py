import logging
from edufox.views import printOutLogs
from django.core.cache import caches, cache
# cache = caches['autocomplete_redis_cache']
key = "query_store"


class Trie:
    is_end: bool = False
    # children: dict[str, object]

    def __init__(self):

        # def __init__(self, store: list[bool, dict]):
        # self.children = {}
        # if not store:
        #     store = {}
        self.children = {}

    def insert(self, word):
        # key = "query_store2"
        # cache = caches['autocomplete_redis_cache']
        # query_store = cache.get(key)
        node = self
        # logging.info("node: ", self)
        # print(("node: ", self.children))
        for ch in word:
            ch = ch.lower()
            if node and ch not in node.children:
                node.children[ch] = Trie()
                # print("node insert: ", node.children)

            node = node.children[ch]

        node.is_end = True
        node = self.children
        print("node after insert: ", node)

        # return node

    def is_word_available(self, word):
        node = self
        for ch in word:
            ch = ch.lower()
            if ch not in node.children:
                return False

            node = node.children[ch]

        return True if node.is_end else False

    def search(self, word):
        # node = self
        node = self
        # printOutLogs(node.children, node.is_end)
        for ch in word:
            # print("word: ", ch, node.children)
            ch = ch.lower()
            if ch not in node.children:
                return None

            print("word: ", ch, node.children)
            node = node.children[ch]

        print("search node: ", node)
        return node if node.is_end else None

    def auto_complete(self, prefix):
        node = self
        for ch in prefix:
            # print("word: ", ch, node.children)
            ch = ch.lower()
            if ch not in node.children:
                return []
            node = node.children[ch]

        return node

    def get_words(self):
        node = self
        # logging.info("node get_words: ", self)
        # key = "query_store2"

        def find_word(node, word: list, words: list):
            if node and node.is_end:
                words.append(''.join(word))
                # logging.info("initial words: ", words)

            for child in node.children:
                # logging.info("child:", child)
                child = child.lower()
                word.append(child)
                find_word(node.children[child], word, words)
                word.pop()

        words = []
        find_word(node, [], words)
        print("final words: ", words)
        return words

    def suggest(self, prefix):
        # node = self
        words = []
        node = self.auto_complete(prefix)
        print("node: ", node)
        try:
            words = [prefix+word for word in node.get_words()]
        except Exception as ex:
            print("suggest error: ", ex)
        return words

    def delete(self, word):
        node = self
        is_found = self.is_word_available(word)

        def recurse(node, word: str, index: int):
            if index == len(word) - 1:
                node.is_end = False
                return len(node.children) == 0
            node = node.children[word[index]]
            is_delete = recurse(node, word, index + 1)
            if is_delete:
                del node.children[word[index]]

            return is_delete and not node.is_end and len(node.children) == 0
        if is_found:
            recurse(node, word, 0)
