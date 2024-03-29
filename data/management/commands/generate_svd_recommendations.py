from collections import defaultdict
from surprise import SVD, SVDpp, NormalPredictor
from surprise import Dataset
from surprise import accuracy
from surprise import Reader
from surprise.model_selection import cross_validate, train_test_split, GridSearchCV
import pandas as pd
from django.core.management.base import BaseCommand
from ...models import *
from users.models import User

class Command(BaseCommand):
    help = 'Generate recommendations'

    def handle(self, *args, **options):

        ratings = Rating.objects.all().values_list('user__id', 'tweet__id', 'rating')

        # Convert tuples to pandas DataFrame
        df_ratings = pd.DataFrame(ratings, columns=["user_id", "tweet_id", "rating"])

        # Reader only needed for rating_scale
        reader = Reader(rating_scale=(1, 5))

        # The columns must correspond to user id, item id and ratings (in that order).
        data = Dataset.load_from_df(df_ratings[['user_id', 'tweet_id', 'rating']], reader)

        # Define the algorithm objects
        algo_SVD = SVD(n_epochs=10, lr_all=0.001, reg_all=1)

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

        trainset, testset = train_test_split(data, test_size=0.2)

        algo_SVD.fit(trainset)

        # Predict ratings for the testset
        predictions_SVD = algo_SVD.test(testset)

        # Compute and print Root Mean Squared Error and Mean Absolute Error
        rmse_SVD = accuracy.rmse(predictions_SVD, verbose=True)
        mae_SVD = accuracy.mae(predictions_SVD, verbose=True)

        top_n_SVD = get_top_n(predictions_SVD, n=10)

        # Print the recommended items for each user and save it to Recommendation model in Django
        for uid, user_ratings in top_n_SVD.items():
            user = User.objects.get(id=uid)
            for iid, _ in user_ratings:
                tweet = Tweets.objects.get(id=iid)
                recommendation = SVDRecommendations(user=user, tweet=tweet)
                recommendation.save()

        print("Running 5-fold cross-validation for SVD...")
        cross_validate(algo_SVD, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
