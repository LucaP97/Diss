from collections import defaultdict
from surprise import SVD, SVDpp, NormalPredictor
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate
from surprise.model_selection import train_test_split
import pandas as pd
from django.core.management.base import BaseCommand
from ...models import *
from users.models import User

class Command(BaseCommand):
    help = 'Generate recommendations'

    def handle(self, *args, **options):

        # Fetch all the records using Django's ORM
        ratings = Rating.objects.all().values_list('user__id', 'tweet__id', 'rating')

        # Fetch all the records using Django's ORM
        ratings = Rating.objects.all().values_list('user__id', 'tweet__id', 'rating')

        # Convert tuples to pandas DataFrame
        df_ratings = pd.DataFrame(ratings, columns=["user_id", "tweet_id", "rating"])

        # A reader is still needed but only the rating_scale param is required.
        reader = Reader(rating_scale=(1, 5))

        # The columns must correspond to user id, item id and ratings (in that order).
        data = Dataset.load_from_df(df_ratings[['user_id', 'tweet_id', 'rating']], reader)

        # Define the algorithm objects
        algo_SVD = SVD()
        algo_SVDpp = SVDpp()
        algo_random = NormalPredictor()

        def get_top_n(predictions, n=10):
            '''
            Returns the top-N recommendation for each user from a set of predictions.
            '''

            # First map the predictions to each user.
            top_n = defaultdict(list)
            for uid, iid, true_r, est, _ in predictions:
                top_n[uid].append((iid, est))

            # Then sort the predictions for each user and retrieve the k highest ones.
            for uid, user_ratings in top_n.items():
                user_ratings.sort(key=lambda x: x[1], reverse=True)
                top_n[uid] = user_ratings[:n]

            return top_n

        # Train on the entire data
        trainset = data.build_full_trainset()

        # Train all algorithms
        algo_SVD.fit(trainset)
        algo_SVDpp.fit(trainset)
        algo_random.fit(trainset)

        # Predict ratings for all pairs (u, i) that are NOT in the training set.
        testset = trainset.build_anti_testset()

        predictions_SVD = algo_SVD.test(testset)

        top_n_SVD = get_top_n(predictions_SVD, n=10)

        # Print the recommended items for each user and save it to Recommendation model in Django
        for uid, user_ratings in top_n_SVD.items():
            user = User.objects.get(id=uid)
            for iid, _ in user_ratings:
                tweet = Tweets.objects.get(id=iid)
                recommendation = Recommendation(user=user, tweet=tweet)
                recommendation.save()
