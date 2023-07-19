from surprise import SVD, SVDpp, NormalPredictor
from surprise import Dataset
from surprise import Reader
from surprise.model_selection import cross_validate
from surprise.model_selection import train_test_split
import pandas as pd
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="toor",
    database="dissdb"
)

cursor = db.cursor()

cursor.execute("SELECT user_id, tweet_id, rating FROM data_rating")

tuples = cursor.fetchall()

# Convert tuples to pandas DataFrame
df_ratings = pd.DataFrame(tuples, columns=["user_id", "tweet_id", "rating"])

cursor.close()
db.close()

# A reader is still needed but only the rating_scale param is required.
reader = Reader(rating_scale=(1, 5))

# The columns must correspond to user id, item id and ratings (in that order).
data = Dataset.load_from_df(df_ratings[['user_id', 'tweet_id', 'rating']], reader)

# Define the algorithm objects
algo_SVD = SVD()
algo_SVDpp = SVDpp()
algo_random = NormalPredictor()

# Run 5-fold cross-validation for each algorithm
print("Running cross-validation for SVD...")
cross_validate(algo_SVD, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

print("Running cross-validation for SVDpp...")
cross_validate(algo_SVDpp, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

print("Running cross-validation for Random...")
cross_validate(algo_random, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
