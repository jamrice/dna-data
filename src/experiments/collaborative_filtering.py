import numpy as np
import pandas as pd

from src.dna_logger import logger
from src.db_handler import get_db_handler

from sklearn.metrics.pairwise import cosine_similarity


class SimilarityScoreGenerator:

    def __init__(self):
        self.db_handler = get_db_handler()
        self.cosine_sim_matrix = self.generate_similarity_score()

    def generate_similarity_score(self):
        # Retrieve the user-bill score data from the database
        metrics = self.db_handler.execute_query("SELECT * FROM user_content_metrics")

        # Create the user-item matrix
        self.user_item_matrix = metrics.pivot_table(
            index="user_id", columns="content_id", values="similarity_score"
        ).fillna(0)

        # Compute the cosine similarity matrix
        return cosine_similarity(self.user_item_matrix)

    def collaborative_filtering_recommendation(self, user_id, k=10):
        user_similarities = self.cosine_sim_matrix[user_id]
        top_k_similar_users = np.argsort(user_similarities)[-k - 1 : -1][::-1]

        # Retrieve user scores from the user-item matrix
        similar_users_scores = self.user_item_matrix.iloc[top_k_similar_users]

        # Calculate mean scores
        mean_scores = similar_users_scores.mean(axis=0)

        # Get top k books based on mean scores
        top_k_bills = mean_scores.sort_values(ascending=False).head(k).index
        return top_k_bills


if __name__ == "__main__":
    pass
