from rest_framework import serializers
from .models import TweetData

class TweetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    text = serializers.CharField()

    class Meta:
        model = TweetData
        fields = ['id', 'text']


# from rest_framework import serializers

class TwitterUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    followers_count = serializers.IntegerField()


class TweetSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=280)
    created_at = serializers.DateTimeField()
    retweet_count = serializers.IntegerField()
    favourite_count = serializers.IntegerField()
    tweet_url = serializers.URLField()
    media_urls = serializers.ListField(child=serializers.URLField())
    included_urls = serializers.ListField(child=serializers.URLField())  # added this line
    place = serializers.CharField(max_length=200)
    # sentiment = serializers.CharField(max_length=50)  # added this line
    # sentiment_scores = serializers.DictField(child=serializers.FloatField())  # added this line
    key_phrases = serializers.SerializerMethodField()
    entities = serializers.SerializerMethodField()

    def get_key_phrases(self, obj):
        # Each key phrase is a dictionary with 'Score' and 'Text' keys. 
        # We will only return the 'Text' values in a list.
        return [phrase['Text'] for phrase in obj['key_phrases']]

    def get_entities(self, obj):
        # Each entity is a dictionary with several keys. 
        # We will return a list of dictionaries, but only with the 'Type' and 'Text' keys.
        return [{'Type': entity['Type'], 'Text': entity['Text']} for entity in obj['entities']]

