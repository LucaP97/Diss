import numpy as np
import tensorflow as tf
import tensorflow_recommenders as tfrs
# from tensorflow.keras.layers.experimental.preprocessing import StringLookup, Normalization
from tensorflow.keras.layers import StringLookup, Normalization
from sklearn.preprocessing import LabelEncoder
from ...models import *
from users.models import User

# print(len(users))
# print(len(tweets))
# print(len(ratings))
# print(len(favourite_teams))


def create_dataset():
    # Fetch all necessary data from the database
    rating_objects = Rating.objects.all().exclude(user_id=152)  # Exclude the user with id 152

    tweet_ids = [rating.tweet_id for rating in rating_objects]
    tweet_objects = Tweets.objects.filter(id__in=tweet_ids)

    tweet_texts = [rating.tweet.text for rating in rating_objects]
    sentiments = [rating.tweet.sentiment if rating.tweet.sentiment is not None else "NEUTRAL" for rating in rating_objects]

    user_ids = [rating.user_id for rating in rating_objects]
    ratings = [rating.rating for rating in rating_objects]

    # Loop over each rating and get the favourite team of the user who made that rating
    favourite_teams = []
    for rating in rating_objects:
        user_id = rating.user_id
        favourite_team = User.objects.get(id=user_id).profile.favourite_team
        favourite_teams.append(favourite_team)

    data = {
        'user': user_ids,
        'tweet': tweet_ids,
        'rating': ratings,
        'text': tweet_texts,
        'sentiment': sentiments,
        'favourite_team': favourite_teams,
    }
    
    for key, value in data.items():
        print(f"{key}: {len(value)}")

    dataset = tf.data.Dataset.from_tensor_slices(data)
    dataset = dataset.shuffle(len(user_ids)).batch(32)

    return dataset


class UserModel(tf.keras.Model):
    def __init__(self, user_ids, favourite_teams):
        super().__init__()

        self.user_embedding = tf.keras.layers.Embedding(len(np.unique(user_ids)), 32)
        self.favourite_team_embedding = tf.keras.layers.Embedding(len(np.unique(favourite_teams)), 32)

    def call(self, inputs):
        return tf.concat([
            self.user_embedding(inputs["user"]),
            self.favourite_team_embedding(inputs["favourite_team"]),
        ], axis=1)

# class TweetModel(tf.keras.Model):
#     def __init__(self, tweet_texts, sentiments):
#         super().__init__()

#         self.tweet_embedding = tf.keras.layers.Embedding(len(np.unique(tweet_texts)), 32)
#         self.sentiment_embedding = tf.keras.layers.Embedding(len(np.unique(sentiments)), 32)

#     def call(self, inputs):
#         return tf.concat([
#             self.tweet_embedding(inputs["text"]),
#             self.sentiment_embedding(inputs["sentiment"]),
#         ], axis=1)


# class TweetRecommendationModel(tfrs.Model):
#     def __init__(self, user_model, tweet_model, tweet_texts):
#         super().__init__()
#         self.user_model = user_model
#         self.tweet_model = tweet_model
#         self.tweet_dataset = tf.data.Dataset.from_tensor_slices(tweet_texts)
#         self.task = tfrs.tasks.Retrieval(
#             metrics=tfrs.metrics.FactorizedTopK(
#                 candidates=self.tweet_dataset.batch(128).map(self.tweet_model),
#             ),
#         )

class TweetModel(tf.keras.Model):
    def __init__(self, tweet_ids, sentiments):
        super().__init__()
        self.tweet_embedding = tf.keras.layers.Embedding(len(np.unique(tweet_ids)) + 1, 32, mask_zero=True)
        self.sentiment_embedding = tf.keras.layers.Embedding(len(np.unique(sentiments)) + 1, 32, mask_zero=True)

    def call(self, inputs):
        tweet_input = inputs["tweet"]
        sentiment_input = inputs["sentiment"]

        mask = self.tweet_embedding.compute_mask(tweet_input)
        
        return tf.concat([
            self.tweet_embedding(tweet_input),
            self.sentiment_embedding(sentiment_input),
        ], axis=1) * tf.cast(mask, tf.float32)

# class TweetModel(tf.keras.Model):
#     def __init__(self, tweet_ids, sentiments):
#         super().__init__()

#         self.tweet_embedding = tf.keras.layers.Embedding(len(np.unique(tweet_ids)), 32)
#         self.sentiment_embedding = tf.keras.layers.Embedding(len(np.unique(sentiments)), 32)

#     def call(self, inputs):
#         return tf.concat([
#             self.tweet_embedding(inputs["tweet"]),
#             self.sentiment_embedding(inputs["sentiment"]),
#         ], axis=1)

class TweetRecommendationModel(tfrs.Model):
    def __init__(self, user_model, tweet_model, tweet_ids):
        super().__init__()
        self.user_model = user_model
        self.tweet_model = tweet_model
        self.tweet_dataset = tf.data.Dataset.from_tensor_slices(tweet_ids)
        for data in self.tweet_dataset.take(1):
            print('*** HERE ***')
            print(data)
        self.task = tfrs.tasks.Retrieval(
            metrics=tfrs.metrics.FactorizedTopK(
                candidates=self.tweet_dataset.batch(128).map(self.tweet_model),
            ),
        )

    def compute_loss(self, features, training=False):
        user_embeddings = self.user_model({"user": features["user"], "favourite_team": features["favourite_team"]})
        tweet_embeddings = self.tweet_model({"text": features["text"], "sentiment": features["sentiment"]})
        return self.task(user_embeddings, tweet_embeddings)

# Fetch all necessary data from the database
tweet_objects = Tweets.objects.all()
rating_objects = Rating.objects.exclude(user_id=152)  # Exclude the user with id 152

# tweet_texts = [tweet.text for tweet in tweet_objects]
tweet_ids = [tweet.id for tweet in tweet_objects]
sentiments = [tweet.sentiment for tweet in tweet_objects]

user_ids = [rating.user_id for rating in rating_objects]
favourite_teams = [user.profile.favourite_team for user in User.objects.exclude(id=152)]  # Exclude the user with id 152

# Create the dataset
dataset = create_dataset()

# Define your model instances
user_model = UserModel(user_ids, favourite_teams)
# tweet_model = TweetModel(tweet_texts, sentiments)
tweet_model = TweetModel(tweet_ids, sentiments)
# model = TweetRecommendationModel(user_model, tweet_model, tweet_texts)
model = TweetRecommendationModel(user_model, tweet_model, tweet_ids)

# Compiling the model
model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))

# Fit the model
model.fit(dataset, epochs=5)

