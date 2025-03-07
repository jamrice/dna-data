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
        ratings = (
            self.db_handler.get_metric_data()
        )  # Assuming this returns a DataFrame with 'User-ID', 'Bill-Title', and 'user_score'

        # Create the user-item matrix
        user_item_matrix = ratings.pivot_table(
            index="User-ID", columns="Bill-Title", values="user_score"
        ).fillna(0)

        # Compute the cosine similarity matrix
        return cosine_similarity(user_item_matrix)

    def collaborative_filtering_recommendation(self, user_id, k=10):
        user_similarities = self.cosine_sim_matrix[user_id]
        top_k_similar_users = np.argsort(user_similarities)[-k - 1 : -1][::-1]

        # Retrieve user scores instead of ratings
        similar_users_scores = [
            self.db_handler.get_metric(user) for user in top_k_similar_users
        ]

        # Calculate mean scores
        mean_scores = np.mean(similar_users_scores, axis=0)

        # Get top k books based on mean scores
        top_k_bills = mean_scores.sort_values(ascending=False).head(k).index
        return top_k_bills
