import numpy as np
import pandas as pd

from src.dna_logger import logger
from src.db_handler import get_db_handler
from sqlalchemy import text

from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFiltering:

    def __init__(self, user_id):
        self.db_handler = get_db_handler()
        self.cosine_sim_matrix = self.generate_similarity_score()
        self.bills = self.collaborative_filtering_recommendation(user_id)

    # some function to deal with time decomposing for metric_score
    def time_decomposing(self):
        pass

    def generate_similarity_score(self):
        # Retrieve the user-bill score data from the database
        metrics = self.db_handler.db.execute(text("SELECT * FROM user_content_metrics"))
        metrics = (
            pd.DataFrame(metrics, columns=metrics.keys())
            .drop_duplicates(subset="id")
            .set_index("id")
        )
        self.time_decomposing()
        # Create the user-item matrix
        self.user_item_matrix = metrics.pivot_table(
            index="user_id", columns="content_id", values="metric_score"
        ).fillna(0)

        # Compute the cosine similarity matrix
        return cosine_similarity(self.user_item_matrix)

    def collaborative_filtering_recommendation(self, user_id, k=2):
        user_similarities = self.cosine_sim_matrix[user_id]
        top_k_similar_users = np.argsort(user_similarities)[-k - 1 : -1][::-1]

        # Retrieve user scores from the user-item matrix
        similar_users_scores = self.user_item_matrix.iloc[top_k_similar_users]

        # Calculate mean scores
        mean_scores = similar_users_scores.mean(axis=0)

        # Get the bills that the user has already watched
        watched_bills = self.user_item_matrix.loc[user_id][
            self.user_item_matrix.loc[user_id] > 0
        ].index

        # Filter out the watched bills from mean scores
        mean_scores = mean_scores[~mean_scores.index.isin(watched_bills)]

        # Get top k unwatched bills based on mean scores
        top_k_bills = mean_scores.sort_values(ascending=False).head(k).index
        return top_k_bills


if __name__ == "__main__":
    cf = CollaborativeFiltering(1)
    print(cf.bills)
