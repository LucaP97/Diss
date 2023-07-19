from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from jsonfield import JSONField

class Tweets(models.Model):
    text = models.CharField(max_length=400)
    created_at = models.DateTimeField()
    retweet_count = models.IntegerField()
    favorite_count = models.IntegerField()
    tweet_url = models.URLField()
    media_urls = JSONField()
    included_urls = JSONField()
    place = models.CharField(max_length=200, null=True, blank=True)
    sentiment = models.CharField(max_length=50)
    sentiment_scores = JSONField()
    key_phrases = JSONField()
    entities = JSONField()

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=280)
    favourite_team = models.CharField(max_length=280)
    current_location = models.CharField(max_length=280)

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

class SVDRecommendations(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='svd_recommendations')
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE, related_name='svd_recommendations')

class HybridRecommendations(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hybrid_recommendations')
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE, related_name='hybrid_recommendations')

class KNNRecommendations(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='knn_recommendations')
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE, related_name='knn_recommendations')

class TFRSRecommendations(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tfrs_recommendations')
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE, related_name='tfrs_recommendations')