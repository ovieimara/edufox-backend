from abc import abstractmethod, ABC
from genericpath import exists
import json
import logging
import threading
from typing import OrderedDict
from requests import get

from client.library import AmazonDynamoDBRepo
import concurrent.futures

from course.models import Grade, Lesson, Subject, Topic


class TextEditor(ABC):
    def __init__(self, words: str = '') -> None:
        self.words = words

    @abstractmethod
    def get_lesson_title(self, title: str) -> str:
        '''edit the lesson title'''

    @abstractmethod
    def get_video_title_id(self, words: str) -> tuple:
        '''set video title from lesson title and also reset lesson title'''

    @abstractmethod
    def get_video_tag(self, subject: str, topic: str) -> str:
        '''set video tags from lesson, topic, subject text'''


class TitleEditor(TextEditor):
    def get_lesson_title(self, title: str) -> str:
        video_id = ''
        title_arr = title.split('_')
        if len(title_arr) > 1:
            last_word = title_arr.pop(
            ) if "converted.mp4" in title_arr[-1] else ''

            last_arr = last_word.split('-') if last_word else []
            if len(last_arr) > 1:
                _, video_id = last_arr

        if title_arr[-1] and '-' in title_arr[-1]:
            last_title_arr = title_arr[-1].split('-')
            if last_title_arr:
                print(last_title_arr)
                title_arr[-1] = last_title_arr[0]
                video_id = last_title_arr[1] if last_title_arr[1] else ''

        if title_arr[-1] and '.mp4' in title_arr[-1]:
            title_arr[-1] = title_arr[-1][:-4]

        # return f"{' '.join(title_arr).strip().title()}{'-' if video_id else ''}{video_id}"
        return f"{' '.join(title_arr).strip()}{'-' if video_id else ''}{video_id}"

    def get_video_title_id(self, words: str) -> tuple:
        videoId = ''
        arr = words.split('-')
        if len(arr) > 1:
            words, videoId = arr

        self.words = words
        return words, videoId

    def get_video_tag(self, subject: str, topic: str) -> str:
        filtered_words = {
            word for word in self.words.split() if len(word) > 3}
        if subject:
            filtered_words.add(subject)
        if topic:
            filtered_words.add(topic)

        return ', '.join(filtered_words)


class CreateMultipleLessons(TitleEditor):
    '''Edits multiple Lesson title fields for a Lesson'''

    def split_titles_ids(self, lesson: OrderedDict) -> list:
        lessons = []
        try:
            grades = lesson.getlist('grade') if hasattr(
                lesson, 'getlist') else lesson.get('grade')
            titles_arr = lesson.get('title', '').split(',')
            lessons = [{key: val for key, val in lesson.items()}
                       for _ in range(len(titles_arr))]
            for index, title in enumerate(titles_arr):
                # new_lesson = {key: title if key ==
                #               'title' else index + 1 if key == 'num' else value for key, value in lesson.items()}
                lessons[index]['title'] = self.get_lesson_title(title)
                # lessons[index]['title'] = title

                prev_num = lessons[index].get('num')
                lessons[index]['num'] = index + \
                    prev_num if prev_num else index + 1
                lessons[index]['grade'] = grades

        except Exception as ex:
            print(ex)

        return lessons


class BatchVideos():
    def __init__(self) -> None:
        self.videos_list = []
        self.lock = threading.Lock()  # Lock to protect videos_list

    def generate_videos(self, lessons: list) -> list:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(
                self.processLessonAsync, lesson) for lesson in lessons]

            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                pass

        # print('self.videos_list: ', self.videos_list)
        return self.videos_list

    def get_video_data(self, title: str, subject: str) -> tuple[str, str]:
        db = AmazonDynamoDBRepo()
        title = self.editTitle(title)
        return db.getSignedUrlFromScan(title, self.query_object(subject, Subject))

        # return ''
    def editTitle(self, title: str):
        arr = title.split('-')
        if len(arr) > 0:
            # return arr[0].capitalize()
            return arr[0]
        return ''

    def query_object(self, subject: str, object: object):
        subject_code = ''

        subject_queryset = object.objects.all().filter(pk=subject)
        if subject_queryset:
            subject_instance = subject_queryset.first()
            subject_code = subject_instance.code

        return subject_code

    def processLessonAsync(self, lesson: OrderedDict):

        guid, url = self.get_video_data(
            lesson.get('title'), lesson.get('subject'))

        video = dict(lesson)

        video['video_id'] = guid
        video['url'] = url
        video['url2'] = url
        video['end_start_credits'] = "0:07"
        video['lesson'] = video.pop('pk')
        video['lessons'] = lesson.get("title")
        video['topics'] = lesson.get('topic')
        video['duration'] = '0:07'
        video['tags'] = ''
        video['title'] = ''
        video.pop('num')

        with self.lock:
            self.videos_list.append(video)

        logging.error(self.videos_list)
