from functools import partial
import logging
from django.shortcuts import render
from rest_framework import generics, mixins, status
from django.core.cache import caches
from rest_framework.response import Response
from rest_framework.views import APIView
from course.models import Lesson, Topic
import concurrent.futures
from edufox.views import printOutLogs

cache = caches['autocomplete_redis_cache']
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
                printOutLogs("node insert: ", node.children)

            node = node.children[ch]

        node.is_end = True
        node = self.children
        printOutLogs("node after insert: ", node)
        cache.set(key, self)

        # return self

    def is_word_available(self, word):
        node = self
        for ch in word:
            ch = ch.lower()
            if ch not in node.children:
                return False

            node = node.children[ch]

        return True if node.is_end else False

    def search(self, word):
        node = self

        # printOutLogs(node.children, node.is_end)
        for ch in word:
            print("word: ", ch, node.children)
            ch = ch.lower()
            if ch not in node.children:
                return None
            node = node.children[ch]
            printOutLogs("search node: ", node.children)

        return node if node.is_end else None

    def get_words(self, query):
        # node = self
        # logging.info("node get_words: ", self)
        # key = "query_store2"
        node = cache.get(key)
        print('node: ', node)

        def find_word(node, word: list, words: list):
            if node and node.is_end:
                words.append(''.join(word))
                # logging.info("initial words: ", words)

            for child in node.children:
                print("child:", child)
                child = child.lower()
                word.append(child)
                find_word(node.children[child], word, words)
                word.pop()

        words = []

        node = self.search(query)
        # print('get node', node)
        if node:
            find_word(node, [], words)
        # print("final words: ", words)
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


class AutoCompleteAPIView(generics.ListCreateAPIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # key = "query_store2"
        query = request.data.get('query')
        print(query)
        # cache = caches['autocomplete_redis_cache']
        # query_store = caches.get(key, {})
        # # logging.info(query_store)
        query_store = cache.get(key)
        # if query_store:
        #     print("query_store: ", query_store.children['c'])
        # print(query_store)
        # if not query_store:
        #     # cache.set(key, {})
        #     query_store = cache.get(key)
        words = []
        query_store = {}
        trie = Trie()
        setup_trie(trie)
        node = trie.insert(query)

        words = get_words_from_trie(trie, query)

        # node = trie.search(query)
        # if node:
        #     print("query_store: ", query_store.children)

        # words = [query+word for word in words]
        # # cache.set(key, node)
        # # node = trie.search(query)
        # query_store = cache.get(key)
        # print("query_store2: ", query_store.children['c'])
        # print("query_store2: ", query_store.children['c'].children['a'])
        # trie2 = Trie(query_store)
        # words = trie2.get_words(query)
        # printOutLogs("words: ", trie2.children)

        data = {
            "data": words
        }

        return Response(data, status.HTTP_200_OK)


def get_words_from_trie(trie: Trie, query: str) -> list:
    print("trie: ", trie)
    words = trie.get_words(query)
    words = [query.lower()+word for word in words]
    return words


def setup_trie(trie: Trie):
    # key = "query_store"
    # query_store = cache.get(key)
    # trie = Trie(query_store)

    # store = ['car', 'carpet', 'career', 'caterpillar', 'verbs', 'noun',
    #          'carpenter', 'Proper nouns', 'Plural Nouns', 'nounonite', 'nouns gender']
    words = get_words_from_lessons()
    # print('TESSST: ', list(words)[:30])
    process_insert_words_trie(words, trie)
    # [trie.insert(word) for word in list(words)[:30]]


def get_words_from_lessons(grade=None):
    lessons = []
    lessons_queryset = Lesson.objects.all()
    if grade:
        lessons_queryset = lessons_queryset.filter(
            grade__pk=grade).distinct('pk')

    # for lesson in lessons_queryset:
    #     lessons.append(lesson.title)
    lessons = process_lessons(lessons_queryset)
    # print("lessons: ", lessons)
    return lessons


def process_insert_words_trie(words, trie):
    num_threads = 4  # You can adjust this number based on your requirements

    # Use ThreadPoolExecutor to parallelize the operation
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Define a function that retrieves the lesson from a single video
        def insert_word(word, trie):
            try:
                trie.insert(word)

            except Exception as ex:
                print(f"Error while processing video {word}: {ex}")
            return None

        # Create a set to keep track of existing video primary keys
        existing_set = []

        # Use submit to asynchronously submit the tasks to the thread pool
        futures = [executor.submit(
            insert_word, word, trie) for word in words]

        # Use as_completed to retrieve the results as they complete
        # return existing_set


def process_lessons(lessons_queryset):
    num_threads = 4  # You can adjust this number based on your requirements

    # Use ThreadPoolExecutor to parallelize the operation
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Define a function that retrieves the lesson from a single video
        def get_title(lesson, existing_set):
            try:
                if lesson:
                    words = lesson.title.split()
                    for word in words:
                        existing_set.add(word)
                    # return video.lesson
            except Exception as ex:
                print(f"Error while processing video {lesson.title}: {ex}")
            return None

        # Create a set to keep track of existing video primary keys
        existing_set = set()

        # Use submit to asynchronously submit the tasks to the thread pool
        [executor.submit(
            get_title, lesson, existing_set) for lesson in lessons_queryset]

        # Use as_completed to retrieve the results as they complete
        return existing_set


# def process_topic(self, topic, grade=None):
#     lessons_queryset = topic.topic_lessons
#     if grade:
#         lessons_queryset = lessons_queryset.filter(
#             grade__pk=grade).distinct('pk')
#     serialized_lessons = self.get_serializer(
#         lessons_queryset, many=True).data
#     serialized_topic = TopicSerializer(topic).data
#     return {"title": serialized_topic, "data": serialized_lessons}

# def process_topics(lessons_queryset, grade=None):
#     topics_set = set()
#     topics_lessons = []
#     if grade:
#         lessons_queryset = lessons_queryset.filter(
#             grade__pk=grade).distinct('pk')

#     # Function to process each topic concurrently
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_to_topic = {executor.submit(
#             process_topic, lesson, grade) for lesson in lessons_queryset}
#         for future in concurrent.futures.as_completed(future_to_topic):
#             topic = future_to_topic[future]
#             try:
#                 obj = future.result()
#                 if topic.id not in topics_set:
#                     topics_set.add(topic.id)
#                     topics_lessons.append(obj)
#             except Exception as exc:
#                 print(f"Exception occurred while processing topic: {exc}")

#     return topics_lessons
