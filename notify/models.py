from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# client = Client(account_sid, auth_token)

# Create your models here.
class AppMessage(models.Model):
    type = models.CharField(max_length=127, default='SMS')
    description = models.TextField(default='')

class Notify(models.Model):
    user = models.ForeignKey(User, related_name='notifications', null=True, on_delete=models.SET_NULL)
    body = models.TextField(default='')
    from_number = models.CharField(max_length=15, default='')
    to_number = models.CharField(max_length=15, default='')
    type = models.ForeignKey(AppMessage, related_name='messages', null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(db_index=True, null=True, auto_now_add=True)
    date_sent = models.DateTimeField(db_index=True, null=True)
    date_updated =  models.DateTimeField(db_index=True, null=True)
    status = models.CharField(max_length=15, null=True, default='')
    error_code = models.CharField(max_length=15, null=True, default='')
    error_message = models.CharField(max_length=15, null=True, default='')
    sid = models.CharField(max_length=15, null=True, default='')

    def sendMessage(self, client):
        message = client.messages.create(
                     body=self.body,
                     from_=self.from_,
                     to=self.to_
                 )
        self.updateMessage(message)
        
    def updateMessage(self, message):
        self.date_created = self.convertStrToDatetime(message.get('date_created'))
        self.date_sent = self.convertStrToDatetime(message.get('date_sent'))
        self.date_updated = self.convertStrToDatetime(message.get('date_updated'))
        self.status = self.message.get('status')
        self.error_code = self.message.get('error_code')
        self.error_message = self.message.get('error_message')
        self.sid = self.message.get('sid')

    def convertStrToDatetime(self, date_str):
        date_obj = None
        if date_str:
            date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        return date_obj



