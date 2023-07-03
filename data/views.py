from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import tweepy
import json
import boto3
import os
from . import serializers
from .serializers import TweetSerializer
from config import *

# Create your views here.

os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'
os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key_id
os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key

class checkBingApi(APIView):
    def get(self, request):
        url = "https://bing-news-search1.p.rapidapi.com/news/search"

        q = "Manchester United"

        querystring = {"q":q, "freshness":"Day","textFormat":"Raw", "safeSearch":"Off"}

        headers = {
            "X-BingApis-SDK": "true",
            "X-RapidAPI-Key": rapid_api_key,
            "X-RapidAPI-Host": "bing-news-search1.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        # print(response.json())

        return Response(response.json())

api_key = twitter_api_key
api_secret_key = twitter_api_secret_key

access_token = twitter_access_token
access_token_secret = twitter_access_token_secret



auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)

class checkTwitterApi(APIView):
    api = tweepy.API(auth)

    def get(self, request):
        api = tweepy.API(auth)
        
        timeline_tweets = api.home_timeline()
        serializer = serializers.TweetSerializer(timeline_tweets, many=True)

        return Response(serializer.data)
    

from rest_framework.views import APIView
from rest_framework.response import Response
import tweepy
from .serializers import TwitterUserSerializer

class PopularTwitterAccounts(APIView):
    def get(self, request):
        # Don't reassign these values, directly use the global variables
        search_term = request.query_params.get('q', default="arsenal")  # The default term is "football"

        max_users = 100

        auth = tweepy.OAuthHandler(api_key, api_secret_key)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)

        users = api.search_users(q=search_term, count=max_users)

        popular_accounts = {}

        for user in users:
            username = user.screen_name
            followers = user.followers_count
            if username not in popular_accounts:
                popular_accounts[username] = followers

        # Sort the dictionary by follower count
        sorted_popular_accounts = sorted(popular_accounts.items(), key=lambda x: x[1], reverse=True)

        # Convert the list of tuples to list of dictionaries
        sorted_popular_accounts_dict = [{"username": i[0], "followers_count": i[1]} for i in sorted_popular_accounts]

        # Serialize the data
        serializer = TwitterUserSerializer(sorted_popular_accounts_dict, many=True)

        return Response(serializer.data)
    


################################
# tweets for build data set

class SpecificTwitterAccountTweets(APIView):
    def get(self, request):
        screen_name = "FabrizioRomano" # specify the account here

        num_of_tweets = 1 # Number of tweets you want to pull

        auth = tweepy.OAuthHandler(api_key, api_secret_key)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)

        tweets = api.user_timeline(screen_name=screen_name, count=num_of_tweets, tweet_mode='extended')

        comprehend = boto3.client(service_name='comprehend', region_name='eu-west-2')

        # Map the relevant information to a list of dictionaries
        tweet_info = []
        for tweet in tweets:
            # constructing the tweet url
            tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
            
            # getting the media urls if exist
            media_urls = []
            if 'media' in tweet.entities:
                media_urls = [media['media_url_https'] for media in tweet.entities['media']]
            
            # getting the urls included in the tweet
            included_urls = [url['expanded_url'] for url in tweet.entities['urls']]

            # Call Amazon Comprehend for Sentiment Analysis
            # sentiment_response = comprehend.detect_sentiment(Text=tweet.full_text, LanguageCode='en')

            # Call Amazon Comprehend for Key Phrase Extraction and Entity Recognition
            key_phrases = comprehend.detect_key_phrases(Text=tweet.full_text, LanguageCode='en')['KeyPhrases']
            entities = comprehend.detect_entities(Text=tweet.full_text, LanguageCode='en')['Entities']

            # appending the information to the list
            tweet_info.append({
                "text": tweet.full_text,
                "created_at": tweet.created_at,
                "retweet_count": tweet.retweet_count,
                "favourite_count": tweet.favorite_count,
                "tweet_url": tweet_url,
                "media_urls": media_urls,
                "included_urls": included_urls,  # added this line
                "place": tweet.place,
                # "sentiment": sentiment_response['Sentiment'],  # added this line
                # "sentiment_scores": sentiment_response['SentimentScore'],  # added this line
                "key_phrases": key_phrases,
                "entities": entities
            })

        # Assuming you have a serializer that matches the data structure above
        serializer = TweetSerializer(tweet_info, many=True)

        return Response(serializer.data)

