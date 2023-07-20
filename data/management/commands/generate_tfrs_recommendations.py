from django.core.management.base import BaseCommand
from ...models import *
from users.models import User
import numpy as np
import tensorflow as tf
from typing import Dict, Text
import tensorflow_recommenders as tfrs
from tensorflow.keras.layers.experimental.preprocessing import StringLookup

class Command(BaseCommand):
    help = 'Description of your command'

    def handle(self, *args, **options):
        # Rating data
        ratings = Rating.objects.all().exclude(user_id=152)  # Exclude the user with id 152
        # Tweet data
        tweets = Tweets.objects.filter(id__in=[rating.tweet_id for rating in ratings])

        # Convert to lists
        ratings_list = list(ratings.values("tweet_id", "user_id"))
        tweets_list = list(tweets.values_list("id", flat=True))

        # Convert lists of dictionaries to a single dictionary with arrays for each feature
        ratings_dict = {
            "tweet_id": [d["tweet_id"] for d in ratings_list],
            "user_id": [d["user_id"] for d in ratings_list],
        }

        # convert the list of dictionaries into tensors
        ratings_tf = tf.data.Dataset.from_tensor_slices(ratings_dict).map(lambda x: {k: tf.as_string(v) for k, v in x.items()})
        tweets_tf = tf.data.Dataset.from_tensor_slices(tweets_list).map(tf.as_string)

        # Select the basic features
        ratings_tf = ratings_tf.map(lambda x: {
            "tweet_id": x["tweet_id"],
            "user_id": x["user_id"]
        })
        tweets_tf = tweets_tf.map(lambda x: x)

        # Building the vocabularies
        user_ids_vocabulary = StringLookup(mask_token=None)
        user_ids_vocabulary.adapt(ratings_tf.map(lambda x: x["user_id"]))

        tweet_ids_vocabulary = StringLookup(mask_token=None)
        tweet_ids_vocabulary.adapt(tweets_tf)

        class TweetModel(tfrs.Model):

            def __init__(
                    self,
                    user_model: tf.keras.Model,
                    tweet_model: tf.keras.Model,
                    task: tfrs.tasks.Retrieval):
                super().__init__()

                # Set up user and tweet representations.
                self.user_model = user_model
                self.tweet_model = tweet_model

                # Set up a retrieval task.
                self.task = task

            def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
                # Define how the loss is computed.

                user_embeddings = self.user_model(features["user_id"])
                tweet_embeddings = self.tweet_model(features["tweet_id"])

                return self.task(user_embeddings, tweet_embeddings)
            
        # define user and tweet models
        user_model = tf.keras.Sequential([
            user_ids_vocabulary,
            tf.keras.layers.Embedding(user_ids_vocabulary.vocabulary_size(), 64)
        ])
        tweet_model = tf.keras.Sequential([
            tweet_ids_vocabulary,
            tf.keras.layers.Embedding(tweet_ids_vocabulary.vocabulary_size(), 64)
        ])

        # define objectives
        task = tfrs.tasks.Retrieval(metrics=tfrs.metrics.FactorizedTopK(
            tweets_tf.batch(128).map(tweet_model)
            )
        )

        # Create a retrieval model.
        model = TweetModel(user_model, tweet_model, task)
        model.compile(optimizer=tf.keras.optimizers.Adagrad(0.5))

        # Train for 3 epochs.
        model.fit(ratings_tf.batch(4096), epochs=3)

        # Use brute-force search to set up retrieval using the trained representations.
        index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
        index.index_from_dataset(
            tweets_tf.batch(100).map(lambda tweet_id: (tweet_id, model.tweet_model(tweet_id)))
        )

        # Get all users
        user_ids = [user["id"] for user in User.objects.values("id")]

        # For each user
        for user_id in user_ids:

            # Get recommendations.
            _, tweet_ids = index(np.array([str(user_id)]))
            # print(f"Top 3 recommendations for user {user_id}: {tweet_ids[0, :3]}")

            # Retrieve the User instance.
            user_instance = User.objects.get(id=user_id)

            # Save recommendations to the database
            for tweet_id in tweet_ids[0, :10]:
                # Retrieve the Tweets instance.
                tweet_instance = Tweets.objects.get(id=tweet_id.numpy().decode())

                # Create a new TFRSRecommendations instance and save it.
                TFRSRecommendations.objects.create(user=user_instance, tweet=tweet_instance)