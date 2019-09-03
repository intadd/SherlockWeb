from django.db import models

from django.utils import timezone





class userLog(models.Model):

    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    userName = models.CharField(max_length=200)
    ipLog=models.CharField(max_length=32)
    UserAgent=models.CharField(max_length=200)
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    def __str__(self):
        return self.ipLog
# Create your models here.