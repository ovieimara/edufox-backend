from abc import abstractmethod, ABC
import json

from requests import get


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
        last_word = title_arr.pop(
        ) if title_arr and '-' in title_arr[-1] else ''
        arr = last_word.split('-')
        if len(arr) > 1:
            _, video_id = arr

        return f"{' '.join(title_arr).strip().title()}{'-' if video_id else ''}{video_id}"

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

    def split_titles_ids(self, lesson) -> list:
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
                prev_num = lessons[index].get('num')
                lessons[index]['num'] = index + \
                    prev_num if prev_num else index + 1
                lessons[index]['grade'] = grades

        except Exception as ex:
            print(ex)

        return lessons
