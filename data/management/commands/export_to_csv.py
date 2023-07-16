from django.core.management.base import BaseCommand
from data.models import Tweets
import csv
import json

class Command(BaseCommand):
    help = 'Export users and tweets data to CSV'

    def handle(self, *args, **kwargs):
        with open('tweets.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            tweets = Tweets.objects.values_list('id', 'text', 'created_at', 'retweet_count', 'favorite_count', 
                                                'tweet_url', 'media_urls', 'included_urls', 'place', 'sentiment', 
                                                'sentiment_scores', 'key_phrases', 'entities')
            for tweet in tweets:
                writer.writerow([json.dumps(column) if type(column) is dict else column for column in tweet])