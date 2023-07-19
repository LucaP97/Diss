from collections import defaultdict
from surprise import SVD, KNNBasic, Dataset, Reader, accuracy
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

        # Convert tuples to pandas DataFrame
        df_ratings = pd.DataFrame(ratings, columns=["user_id", "tweet_id", "rating"])

        # A reader is still needed but only the rating_scale param is required.
        reader = Reader(rating_scale=(1, 5))

        # The columns must correspond to user id, item id and ratings (in that order).
        data = Dataset.load_from_df(df_ratings[['user_id', 'tweet_id', 'rating']], reader)

        # Define the algorithm objects
        algo_SVD = SVD()
        algo_KNN = KNNBasic(sim_options={'name': 'pearson_baseline', 'user_based': True})  # User-based KNN

        # Split the dataset into training set and test set
        trainset, testset = train_test_split(data, test_size=0.2)

        # Train all algorithms on the training set
        algo_SVD.fit(trainset)
        algo_KNN.fit(trainset)

        # Test on the testset
        predictions_SVD = algo_SVD.test(testset)
        predictions_KNN = algo_KNN.test(testset)

        print('SVD RMSE:', accuracy.rmse(predictions_SVD))
        print('SVD MAE:', accuracy.mae(predictions_SVD))
        print('KNN RMSE:', accuracy.rmse(predictions_KNN))
        print('KNN MAE:', accuracy.mae(predictions_KNN))

        # Predict ratings for all pairs (u, i) that are NOT in the training set.
        antitestset = trainset.build_anti_testset()

        predictions_SVD_antitestset = algo_SVD.test(antitestset)  # Get predictions from SVD
        predictions_KNN_antitestset = algo_KNN.test(antitestset)  # Get predictions from User-based KNN

        # Combine predictions
        combined_predictions = []

        for prediction_svd, prediction_knn in zip(predictions_SVD_antitestset, predictions_KNN_antitestset):
            # Average predicted ratings
            avg_rating = (prediction_svd.est + prediction_knn.est) / 2
            combined_predictions.append((prediction_svd.uid, prediction_svd.iid, avg_rating))

        top_n_combined = self.get_top_n(combined_predictions, n=10)  # Get top 10 recommendations from combined predictions

        # Print the recommended items for each user and save it to Recommendation model in Django
        for uid, user_ratings in top_n_combined.items():
            user = User.objects.get(id=uid)
            for iid, _ in user_ratings:
                tweet = Tweets.objects.get(id=iid)
                recommendation = HybridRecommendations(user=user, tweet=tweet)
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
