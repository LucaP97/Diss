from django.core.management.base import BaseCommand, CommandError
import tweepy
from ...models import Tweets
import boto3

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import your module
from config import *

# put your Twitter keys and tokens here
api_key = twitter_api_key
api_secret_key = twitter_api_secret_key
access_token = twitter_access_token
access_token_secret = twitter_access_token_secret

class Command(BaseCommand):
    help = 'Fetches tweets and save them in the database'

    def handle(self, *args, **options):
        auth = tweepy.OAuthHandler(api_key, api_secret_key)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)
        teams = [
            'Arsenal',
            'Aston Villa',
            'Bournemouth',
            'Brentford',
            'Brighton and Hove Albion',
            'Burnley',
            'Chelsea',
            'Crystal Palace',
            'Everton',
            'Fulham',
            'Liverpool',
            'Luton Town',
            'Manchester City',
            'Manchester United',
            'Newcastle United',
            'Nottingham Forest',
            'Sheffield United',
            'Tottenham Hotspur',
            'West Ham United',
            'Wolverhampton Wanderers'
        ]

        num_of_tweets = 200 

        comprehend = boto3.client(service_name='comprehend', region_name='eu-west-2')

        for team in teams:
            tweets = tweepy.Cursor(api.search,
                   q=team,
                   lang="en",
                   tweet_mode='extended').items(num_of_tweets)

            for tweet in tweets:
                tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                media_urls = []
                if 'media' in tweet.entities:
                    media_urls = [media['media_url_https'] for media in tweet.entities['media']]
                included_urls = [url['expanded_url'] for url in tweet.entities['urls']]

                # sentiment_response = comprehend.detect_sentiment(Text=tweet.full_text, LanguageCode='en')

                # key_phrases = comprehend.detect_key_phrases(Text=tweet.full_text, LanguageCode='en')['KeyPhrases']
                # entities = comprehend.detect_entities(Text=tweet.full_text, LanguageCode='en')['Entities']

                # def preprocess_key_phrases(key_phrases):
                #     return [phrase['Text'] for phrase in key_phrases]

                # def preprocess_entities(entities):
                #     return [{'Type': entity['Type'], 'Text': entity['Text']} for entity in entities]

                # processed_key_phrases = preprocess_key_phrases(key_phrases)
                # processed_entities = preprocess_entities(entities)

                Tweets.objects.create(
                    text = tweet.full_text,
                    created_at = tweet.created_at,
                    retweet_count = tweet.retweet_count,
                    favorite_count = tweet.favorite_count,
                    tweet_url = tweet_url,
                    media_urls = media_urls,
                    included_urls = included_urls,
                    place = tweet.place.name if tweet.place else None,
                    # sentiment = sentiment_response['Sentiment'],
                    # sentiment_scores = sentiment_response['SentimentScore'],
                    # key_phrases = processed_key_phrases,
                    # entities = processed_entities
                )
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched tweets for {team}'))