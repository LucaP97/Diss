from collections import defaultdict
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import GridSearchCV, train_test_split
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

        reader = Reader(rating_scale=(1, 5))

        data = Dataset.load_from_df(df_ratings[['user_id', 'tweet_id', 'rating']], reader)

        param_grid = {'n_epochs': [3, 10], 'lr_all': [0.001, 0.020],
                      'reg_all': [0.2, 1]}
        
        gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=5)

        gs.fit(data)

        print(gs.best_score['rmse'])
        print(gs.best_params['rmse'])

        algo_SVD = gs.best_estimator['rmse']

        trainset, testset = train_test_split(data, test_size=0.2)

        algo_SVD.fit(trainset)

        predictions_SVD = algo_SVD.test(testset)

        print('SVD RMSE:', accuracy.rmse(predictions_SVD))
        print('SVD MAE:', accuracy.mae(predictions_SVD))

        top_n_SVD = self.get_top_n(predictions_SVD, n=10)

        # Just print the recommendations without saving to DB
        # for uid, user_ratings in top_n_SVD.items():
        #     print(f"User {uid}:")
        #     for iid, rating in user_ratings:
        #         print(f"\tItem {iid} with predicted rating {rating}")

    def get_top_n(self, predictions, n=10):
        '''Return the top-N recommendation for each user from a set of predictions.'''

        top_n = defaultdict(list)
        for prediction in predictions:
            top_n[prediction.uid].append((prediction.iid, prediction.est))

        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n
