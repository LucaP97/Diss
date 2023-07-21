from rest_framework import serializers
from .models import *
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

###################
# User and Profile
###################

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'date_of_birth', 'place_of_birth', 'favourite_team', 'current_location']
        # 'user',

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

class ProfileRegistrationSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    favourite_team = serializers.ChoiceField(
        choices=[
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
            'Nottinham Forest',
            'Sheffield United',
            'Tottenham Hotspur',
            'West Ham United',
            'Wolverhampton Wanderers'
        ]
    )

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['first_name'] = user_data.pop('first_name')
        user_data['last_name'] = user_data.pop('last_name')

        user_serializer = UserCreateSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        return Profile.objects.create(user=user, **validated_data)
    
    class Meta:
        model = Profile
        fields = ['user', 'date_of_birth', 'place_of_birth', 'favourite_team', 'current_location']


###################
# Ratings
###################

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user', 'tweet', 'rating', 'created_at']

    

class RatingSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        # fields = ['tweet_id', 'user_id', 'rating']
        fields = ['rating']

    def create(self, validated_data):
        tweet_id = self.context['tweet_id']
        user_id = self.context['user_id']
        return Rating.objects.create(user_id=user_id, tweet_id=tweet_id, **validated_data)


###################
# Tweets
###################

class TweetSerializer(serializers.ModelSerializer):
    ratings = RatingSerializer(many=True, read_only=True)

    class Meta:
        model = Tweets
        fields = ['id', 'text', 'created_at', 'retweet_count', 'favorite_count', 'tweet_url', 'media_urls', 'included_urls', 'place', 'sentiment', 'sentiment_scores', 'key_phrases', 'entities', 'ratings']

class TweetSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweets
        fields = ['id', 'text', 'created_at', 'retweet_count', 'favorite_count', 'tweet_url', 'media_urls', 'included_urls']


###################
# Recommendations
###################

class SVDRecommendationSerializer(serializers.ModelSerializer):
    tweet = TweetSimpleSerializer()
    class Meta:
        model = SVDRecommendations
        fields = ['id', 'user', 'tweet']

class HybridRecommendationSerializer(serializers.ModelSerializer):
    tweet = TweetSimpleSerializer()
    class Meta:
        model = SVDRecommendations
        fields = ['id', 'user', 'tweet']

class KNNRecommendationSerializer(serializers.ModelSerializer):
    tweet = TweetSimpleSerializer()
    class Meta:
        model = SVDRecommendations
        fields = ['id', 'user', 'tweet']

class TFRSRecommendationSerializer(serializers.ModelSerializer):
    tweet = TweetSimpleSerializer()
    class Meta:
        model = SVDRecommendations
        fields = ['id', 'user', 'tweet']

