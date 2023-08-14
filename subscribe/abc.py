from abc import ABC, abstractmethod
from course.models import Video

from subscribe.models import Subscribe
from django.utils import timezone
from django.db.models import Q


class UserSubscriptionABC(ABC):
    def __init__(self, user: str, video_id: str = '') -> None:
        self.user = user
        self.video_id = video_id

    @abstractmethod
    def get_user_subscriptions(self):
        """ fetch subscriptions that are valid after timezone.now"""

    @abstractmethod
    def isValidSubForVideo(self) -> bool:
        """check if subscription is valid for a video"""

    @abstractmethod
    def get_all_user_subscriptions(self):
        """return all subscriptions for this user"""


class MySubscription(UserSubscriptionABC):

    def get_user_subscriptions(self):
        return self.user.subscriptions_user.filter(Q(payment_method__expires_date__gt=timezone.now())).order_by("-created")

    def get_all_user_subscriptions(self):
        # print('subscriptions: ', self.user.subscriptions_user)
        queryset = Subscribe.objects.all()
        return queryset.filter(payment_method__expires_date__gt=timezone.now(), user=self.user).order_by("-created") if self.user.is_authenticated else []

    def get_video_grades(self) -> list:
        video_grades = {}
        try:
            video_queryset = Video.objects.filter(video_id=self.video_id)
            if video_queryset.exists():
                video_obj = video_queryset.first()
                grades = video_obj.grade.all()
                video_grades = {grade.pk for grade in grades}
        except Exception as ex:
            print('video object error: ', ex)

        return video_grades

    def isValidSubForVideo(self) -> bool:
        subscriptions = self.get_all_user_subscriptions()
        if subscriptions:
            video_grades = self.get_video_grades()
            for sub in subscriptions.all():
                subscription_grades = set(sub.grade.grades)
                grades_intersection = subscription_grades & video_grades
                print(grades_intersection, subscription_grades, video_grades)

                if grades_intersection:
                    return True
        return False

        # subscriptions = subscriptions.objects.filter(
        #     grade__grades__contains=values)
        # print("subscriptions: ", subscriptions.all(),
        #       self.get_video_grades(), type(self.get_video_grades()))

        # if subscriptions.exists():
        # subscription_obj = subscriptions.filter(
        #     # Q(grade__grades__contains=self.get_video_grades()) &
        #     Q(
        #         payment_method__expires_date__gt=timezone.now())
        # )
        # print("subscriptions2: ", subscription_obj)
        # if subscription_obj.exists():
        # return True
