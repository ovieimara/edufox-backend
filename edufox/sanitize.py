from abc import ABC, abstractmethod
from django.utils.html import escape
from bleach import clean


class Sanitizer(ABC):
    @abstractmethod
    def sanitize_field(self, value: any):
        '''sanitize a value'''

    @abstractmethod
    def sanitize_fields(self, fields: dict):
        '''sanitize a dictionary'''


class BleachSanitizer(Sanitizer):
    def sanitize_field(self, value) -> any:
        return clean(value) if value else value

    def sanitize_fields(self, fields: dict) -> dict:
        return {key: self.sanitize_field(value) if isinstance(value, str) else value for key, value in fields.items()}


class Cleanup():
    def sanitize_attr(self, attrs: dict, sanitizer: Sanitizer):
        return sanitizer.sanitize_fields(attrs)
