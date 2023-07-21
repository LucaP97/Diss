from rest_framework import status
from rest_framework.test import APIClient
import pytest

@pytest.mark.django_db
class TestCreateTweet:
    def test_tweet_post_bad_request(self):
        # Arrange

        # Act
        client = APIClient()
        response = client.post('/data/tweets/', {'text': 'test tweet'}, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_tweet_post_good_request(self):
        # Arrange
        data = {
        "id": 1,
        "text": "a",
        "created_at": "2023-07-09T17:43:11Z",
        "retweet_count": 1,
        "favorite_count": 1,
        "tweet_url": "https://twitter.com/Arsenal/status/1678097478191570946",
        "media_urls": "['https://pbs.twimg.com/media/F0nMlbtXsAEZy6D.jpg']",
        "included_urls": "[]",
        "place": None,
        "sentiment": "NEUTRAL",
        "sentiment_scores": "{'Positive': 0.006695329677313566, 'Negative': 0.0020031346939504147, 'Neutral': 0.9912241697311401, 'Mixed': 7.736184488749132e-05}",
        "key_phrases": "['Next stop']",
        "entities": "[{'Type': 'LOCATION', 'Text': 'Germany'}, {'Type': 'OTHER', 'Text': 'https://t.co/v1bOocbi1C'}]",
    }

        # Act
        client = APIClient()
        response = client.post('/data/tweets/', data, format='json')

        # Assert
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestGetTweets:
    def test_get_tweets(self):
        # Arrange

        # Act
        client = APIClient()
        response = client.get('/data/tweets/')

        # Assert
        assert response.status_code == status.HTTP_200_OK

    def test_get_tweets_by_id(self):
        # Arrange

        # Act
        client = APIClient()
        response = client.get('/data/tweets/1/')

        # Assert
        assert response.status_code == status.HTTP_200_OK


