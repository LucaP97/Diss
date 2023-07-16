from collections import defaultdict
from surprise import SVD, KNNBasic, Dataset, Reader, accuracy
from surprise.model_selection import cross_validate, train_test_split
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from ...models import *
from users.models import User

class Command(BaseCommand):
    help = 'Generate recommendations'

    def handle(self, *args, **options):

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
        algo_KNN = KNNBasic(sim_options={'name': 'pearson_baseline', 'user_based': False})  # Item-based KNN

        # Train on the entire data
        trainset = data.build_full_trainset()

        # Train all algorithms
        algo_SVD.fit(trainset)
        algo_KNN.fit(trainset)  # Train Item-based KNN

        # Predict ratings for all pairs (u, i) that are NOT in the training set.
        testset = trainset.build_anti_testset()

        predictions_SVD = algo_SVD.test(testset)  # Get predictions from SVD
        predictions_KNN = algo_KNN.test(testset)  # Get predictions from Item-based KNN

        print('SVD RMSE:', accuracy.rmse(predictions_SVD))
        print('SVD MAE:', accuracy.mae(predictions_SVD))
        print('KNN RMSE:', accuracy.rmse(predictions_KNN))
        print('KNN MAE:', accuracy.mae(predictions_KNN))

        # Combine predictions
        combined_predictions = []

        for prediction_svd, prediction_knn in zip(predictions_SVD, predictions_KNN):
            # Average predicted ratings
            avg_rating = (prediction_svd.est + prediction_knn.est) / 2
            combined_predictions.append((prediction_svd.uid, prediction_svd.iid, avg_rating))

        # Compute RMSE and MAE for the combined predictions
        true_and_pred = [(pred[2], (pred_svd.est + pred_knn.est) / 2)
                         for pred, pred_svd, pred_knn in zip(combined_predictions, predictions_SVD, predictions_KNN)]
        hybrid_rmse = np.sqrt(np.mean([(true - pred) ** 2 for true, pred in true_and_pred]))
        hybrid_mae = np.mean([abs(true - pred) for true, pred in true_and_pred])
        print('Hybrid RMSE:', hybrid_rmse)
        print('Hybrid MAE:', hybrid_mae)

        top_n_combined = self.get_top_n(combined_predictions, n=10)  # Get top 10 recommendations from combined predictions

        # Print the recommended items for each user and save it to Recommendation model in Django
        for uid, user_ratings in top_n_combined.items():
            user = User.objects.get(id=uid)
            for iid, _ in user_ratings:
                tweet = Tweets.objects.get(id=iid)
                recommendation = Recommendation(user=user, tweet=tweet)
                recommendation.save()

    def get_top_n(self, predictions, n=10):
        '''Return the top-N recommendation for each user from a set of predictions.'''

        # First map the predictions to each user.
        top_n = defaultdict(list)
        for uid, iid, true_r in predictions:
            top_n[uid].append((iid, true_r))

        # Then sort the predictions for each user and retrieve the k highest ones.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n
