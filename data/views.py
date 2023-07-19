from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter 
from rest_framework.decorators import action
from rest_framework import status
import requests
import tweepy
import json
import boto3
import os
from .serializers import *
from .models import *
from config import *

# Create your views here.

# os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'
# os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key_id
# os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key

# class checkBingApi(APIView):
#     def get(self, request):
#         url = "https://bing-news-search1.p.rapidapi.com/news/search"

#         q = "Manchester United"

#         querystring = {"q":q, "freshness":"Day","textFormat":"Raw", "safeSearch":"Off"}

#         headers = {
#             "X-BingApis-SDK": "true",
#             "X-RapidAPI-Key": rapid_api_key,
#             "X-RapidAPI-Host": "bing-news-search1.p.rapidapi.com"
#         }

#         response = requests.get(url, headers=headers, params=querystring)

#         # print(response.json())

#         return Response(response.json())

# api_key = twitter_api_key
# api_secret_key = twitter_api_secret_key

# access_token = twitter_access_token
# access_token_secret = twitter_access_token_secret



# auth = tweepy.OAuthHandler(api_key, api_secret_key)
# auth.set_access_token(access_token, access_token_secret)

# class checkTwitterApi(APIView):
#     api = tweepy.API(auth)

#     def get(self, request):
#         api = tweepy.API(auth)
        
#         timeline_tweets = api.home_timeline()
#         serializer = serializers.TweetSerializer(timeline_tweets, many=True)

#         return Response(serializer.data)
    


# class PopularTwitterAccounts(APIView):
#     def get(self, request):
#         # Don't reassign these values, directly use the global variables
#         search_term = request.query_params.get('q', default="arsenal")  # The default term is "football"

#         max_users = 100

#         auth = tweepy.OAuthHandler(api_key, api_secret_key)
#         auth.set_access_token(access_token, access_token_secret)

#         api = tweepy.API(auth)

#         users = api.search_users(q=search_term, count=max_users)

#         popular_accounts = {}

#         for user in users:
#             username = user.screen_name
#             followers = user.followers_count
#             if username not in popular_accounts:
#                 popular_accounts[username] = followers

#         # Sort the dictionary by follower count
#         sorted_popular_accounts = sorted(popular_accounts.items(), key=lambda x: x[1], reverse=True)

#         # Convert the list of tuples to list of dictionaries
#         sorted_popular_accounts_dict = [{"username": i[0], "followers_count": i[1]} for i in sorted_popular_accounts]

#         # Serialize the data
#         serializer = TwitterUserSerializer(sorted_popular_accounts_dict, many=True)

#         return Response(serializer.data)
    


# ################################
# # tweets for build data set

# class SpecificTwitterAccountTweets(APIView):
#     def get(self, request):
#         screen_name = "TalkingWolves" # specify the account here

#         num_of_tweets = 200 # Number of tweets you want to pull

#         auth = tweepy.OAuthHandler(api_key, api_secret_key)
#         auth.set_access_token(access_token, access_token_secret)

#         api = tweepy.API(auth)

#         tweets = api.user_timeline(screen_name=screen_name, count=num_of_tweets, tweet_mode='extended')

#         comprehend = boto3.client(service_name='comprehend', region_name='eu-west-2')

#         # Map the relevant information to a list of dictionaries
#         tweet_info = []
#         for tweet in tweets:
#             # constructing the tweet url
#             tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
            
#             # getting the media urls if exist
#             media_urls = []
#             if 'media' in tweet.entities:
#                 media_urls = [media['media_url_https'] for media in tweet.entities['media']]
            
#             # getting the urls included in the tweet
#             included_urls = [url['expanded_url'] for url in tweet.entities['urls']]

#             # Call Amazon Comprehend for Sentiment Analysis
#             sentiment_response = comprehend.detect_sentiment(Text=tweet.full_text, LanguageCode='en')

#             # Call Amazon Comprehend for Key Phrase Extraction and Entity Recognition
#             key_phrases = comprehend.detect_key_phrases(Text=tweet.full_text, LanguageCode='en')['KeyPhrases']
#             entities = comprehend.detect_entities(Text=tweet.full_text, LanguageCode='en')['Entities']

#             # appending the information to the list
#             tweet_info.append({
#                 "text": tweet.full_text,
#                 "created_at": tweet.created_at,
#                 "retweet_count": tweet.retweet_count,
#                 "favorite_count": tweet.favorite_count,
#                 "tweet_url": tweet_url,
#                 "media_urls": media_urls,
#                 "included_urls": included_urls,  # added this line
#                 "place": tweet.place,
#                 "sentiment": sentiment_response['Sentiment'],  # added this line
#                 "sentiment_scores": sentiment_response['SentimentScore'],  # added this line
#                 "key_phrases": key_phrases,
#                 "entities": entities
#             })

#             def preprocess_key_phrases(key_phrases):
#                 return [phrase['Text'] for phrase in key_phrases]
            
#             def preprocess_entities(entities):
#                 return [{'Type': entity['Type'], 'Text': entity['Text']} for entity in entities]

#             processed_key_phrases = preprocess_key_phrases(key_phrases)
#             processed_entities = preprocess_entities(entities)

#             Tweets.objects.create(
#                 text = tweet.full_text,
#                 created_at = tweet.created_at,
#                 retweet_count = tweet.retweet_count,
#                 favorite_count = tweet.favorite_count,
#                 tweet_url = tweet_url,
#                 media_urls = media_urls,
#                 included_urls = included_urls,
#                 place = tweet.place,
#                 sentiment = sentiment_response['Sentiment'],
#                 sentiment_scores = sentiment_response['SentimentScore'],
#                 key_phrases = processed_key_phrases,
#                 entities = processed_entities
#             )

#         serializer = TweetSerializer(tweet_info, many=True)

#         return Response(serializer.data)
    
# class AllTweetsViewSet(ModelViewSet):
#     queryset = Tweets.objects.all()
#     serializer_class = AllTweetsSerializer
    

class ProfileViewSet(ModelViewSet):
    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_superuser:
            return Profile.objects.all()
        if self.request.user.is_authenticated:
            return Profile.objects.filter(user=self.request.user)
        else:
            return status.HTTP_401_UNAUTHORIZED

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProfileRegistrationSerializer
        return ProfileSerializer
        

class RatingViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        return Rating.objects.filter(tweet_id=self.kwargs['tweet_pk'])

    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return RatingSimpleSerializer
        return RatingSerializer
    
    def get_serializer_context(self):
        return {'tweet_id': self.kwargs['tweet_pk'], 'user_id': self.request.user.id}
    


class TweetViewSet(ModelViewSet):
    http_method_names = ['get']
    
    queryset = Tweets.objects.all().prefetch_related('ratings')
    serializer_class = TweetSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['created_at', 'sentiment']
    search_fields = ['text', 'key_phrases', 'entities']
    
    pagination_class = PageNumberPagination



###################
# Recommendations
###################

class RecommendationsViewSet(ModelViewSet):
    http_method_names = ['get']
    
    # queryset = Recommendation.objects.all().prefetch_related('tweet__ratings')
    # queryset = Recommendation.objects.filter(user=self.request.user).prefetch_related('tweet__ratings')

    def get_queryset(self):
        # return Recommendation.objects.filter(user=self.request.user).prefetch_related('tweet__ratings')
        return SVDRecommendations.objects.filter(user_id=155).prefetch_related('tweet__ratings')

    serializer_class = SVDRecommendationSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']

    # pagination_class = PageNumberPagination


# frontend
from django.shortcuts import render
# from rest_framework_jwt.utils import jwt_decode_handler

def recommendations_page(request):
    print('is authenticated: ' + str(request.user.is_authenticated))
    # does not work, I cannot authenticate myself on the frontend
    if request.user.is_authenticated:
        recommendations = SVDRecommendations.objects.filter(user_id=request.user.id).prefetch_related('tweet__ratings')
    else:
        # recommendations = []
        recommendations = SVDRecommendations.objects.all().prefetch_related('tweet__ratings')
    return render(request, 'recommendations_page.html', {'recommendations': recommendations})

