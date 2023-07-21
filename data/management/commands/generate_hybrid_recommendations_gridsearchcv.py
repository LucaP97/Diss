from collections import defaultdict
from surprise import SVD, KNNBasic, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split, GridSearchCV
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

        # A reader is still needed but only the rating_scale param is required.
        reader = Reader(rating_scale=(1, 5))

        # The columns must correspond to user id, item id and ratings (in that order).
        data = Dataset.load_from_df(df_ratings[['user_id', 'tweet_id', 'rating']], reader)

        param_grid_svd = {
            "n_epochs": [5, 10, 20],
            "lr_all": [0.002, 0.005, 0.01],
            "reg_all": [0.2, 0.4, 0.6]
        }

        param_grid_knn = {
            "k": [20, 40, 60],
            "sim_options": {
                "name": ["msd", "cosine", "pearson_baseline"],
                "user_based": [False, True],
            }
        }

        gs_svd = GridSearchCV(SVD, param_grid_svd, measures=["rmse", "mae"], cv=3)
        gs_svd.fit(data)

        gs_knn = GridSearchCV(KNNBasic, param_grid_knn, measures=["rmse", "mae"], cv=3)
        gs_knn.fit(data)

        # Get the best parameters
        print(gs_svd.best_params["rmse"])
        print(gs_knn.best_params["rmse"])

        # Then use these parameters for the respective algorithms
        algo_SVD = SVD(**gs_svd.best_params["rmse"])
        algo_KNN = KNNBasic(**gs_knn.best_params["rmse"])

        trainset, testset = train_test_split(data, test_size=0.2)

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

        predictions_SVD_antitestset = algo_SVD.test(antitestset)
        predictions_KNN_antitestset = algo_KNN.test(antitestset)

        # Combine predictions
        combined_predictions = []

        for prediction_svd, prediction_knn in zip(predictions_SVD_antitestset, predictions_KNN_antitestset):
            # Average predicted ratings
            avg_rating = (prediction_svd.est + prediction_knn.est) / 2
            combined_predictions.append((prediction_svd.uid, prediction_svd.iid, avg_rating))

        top_n_combined = self.get_top_n(combined_predictions, n=10)  # Get top 10 recommendations from combined predictions

        # Print the recommended items for each user
        # for uid, user_ratings in top_n_combined.items():
        #     print(f'Recommendations for user {uid}:')
        #     for iid, rating in user_ratings:
        #         print(f'Tweet {iid} with predicted rating {rating}')

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
