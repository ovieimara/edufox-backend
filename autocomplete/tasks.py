import concurrent.futures
from django.core.cache import caches, cache
# cache = caches['autocomplete_redis_cache']
key = "query_store"


def my_background_task():
    print("Background task is running!")
    from .Trie import Trie

    trie = Trie()
    setup_trie(trie)

    # query = 'e'
    # words = get_words_from_trie(trie, query)
    # print("trie: ", words)


def get_words_from_trie(trie, query: str) -> list:

    words = trie.get_words(query)
    words = [query.lower()+word for word in words]
    return words


def setup_trie(trie):

    words = get_words_from_lessons()
    # print(words)
    process_insert_words_trie(list(words), trie)


def get_words_from_lessons(grade=None):
    from course.models import Lesson

    lessons_queryset = Lesson.objects.all()
    if grade:
        lessons_queryset = lessons_queryset.filter(
            grade__pk=grade).distinct('pk')

    words = process_lessons(lessons_queryset)
    return words


def process_insert_words_trie(words, trie):
    num_threads = 4  # Adjust based on your requirements

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        def insert_word(word, trie):
            try:
                trie.insert(word)
            except Exception as ex:
                print(f"Error while inserting word {word}: {ex}")

        # Use submit to asynchronously submit the tasks to the thread pool
        futures = [executor.submit(insert_word, word, trie) for word in words]

        # Wait for all futures to complete
        concurrent.futures.wait(futures)
    cache.set(key, trie)
    # return trie


def process_lessons(lessons_queryset):
    num_threads = 4  # Adjust based on your requirements

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        def get_words_from_lesson(lesson):
            words = set()
            try:
                if lesson:
                    words.update(lesson.title.split())
            except Exception as ex:
                print(f"Error while processing lesson {lesson.title}: {ex}")
            return words

        # Use submit to asynchronously submit the tasks to the thread pool
        futures = [executor.submit(get_words_from_lesson, lesson)
                   for lesson in lessons_queryset]

        # Collect words from all lessons
        words = set()
        for future in concurrent.futures.as_completed(futures):
            words.update(future.result())

        return words
