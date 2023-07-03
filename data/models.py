from django.db import models

# Create your models here.
class SearchData(models.Model):
    pass

class TweetData(models.Model):
    # Id = models.IntegerField()
    Text = models.CharField(max_length=280)