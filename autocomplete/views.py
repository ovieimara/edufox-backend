from django.shortcuts import render
from rest_framework import generics, mixins, status
from django.core.cache import caches
from rest_framework.response import Response
from rest_framework.views import APIView


class Trie:
    # is_end : bool = False
    # children: dict[str, object]

    def __int__(self, store: list[bool, dict]):
        # self.children = {}
        self.children = store

    def insert(self, word):
        node = self.children
        for ch in word:
            if ch not in node[1]:
                node[1][ch] = [False, {}]

            node = node[1][ch]
        node[0] = True

    def is_word_available(self, word):
        node = self.children
        for ch in word:
            if ch not in node[1]:
                return False

            node = node[1][ch]

        return True if node[0] else False

    def search(self, word):
        node = self.children
        for ch in word:
            if ch not in node[1]:
                return None
            node = node[1][ch]

        return node if node[0] else None

    def get_words(self, word):
        node = self.children

        def find_word(node, word: list, words: list):
            if node[0]:
                words.append(''.join(word))
            for child in node[1]:
                word.append(child)
                find_word(node[1][child], word, words)
                word.pop()
        words = []
        node = self.search(word)
        find_word(node, [], words)

        return words

    def delete(self, word):
        node = self.children
        is_found = self.is_word_available(word)

        def recurse(node, word: str, index: int):
            if index == len(word) - 1:
                node[0] = False
                return len(node[1]) == 0
            node = node[1][word[index]]
            is_delete = recurse(node, word, index + 1)
            if is_delete:
                del node[1][word[index]]

            return is_delete and not node[0] and len(node[1]) == 0
        if is_found:
            recurse(node, word, 0)


# Create your views here.
class AutoComplete(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        key = "query_store"
        query = request.data.get('query')
        cache = caches['autocomplete_redis_cache']
        query_store = cache.get(key)

        if not query_store:
            cache.set(key, [False, {}])
            # cache.set(key, [False, {}], cache='autocomplete_redis_cache')
            query_store = cache.get(key)

        trie = Trie(query_store)
        words = trie.get_words(query)
        new_words = [query+word for word in words]

        data = {
            data: new_words
        }
        trie.insert(query)
        return Response(data, status.HTTP_200_OK)
