import numpy as np
import pandas as pd
from datetime import datetime
from src.dna_logger import logger
from src.db_handler import get_db_handler
from sqlalchemy import text
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split


class CollaborativeFiltering:
    def __init__(self):
        self.db_handler = get_db_handler()
        self.metrics = self.get_metrics()
        self.full_matrix = self.metrics.pivot_table(
            index="user_id", columns="content_id", values="metric_score"
        )
        self.user_cosine_similarity = self.calculate_cosine_similarity()
        self.x_train, self.x_test, self.y_train, self.y_test = self._train_test_split()

    def get_metrics(self):
        metrics = self.db_handler.db.execute(text("SELECT * FROM user_content_metrics"))
        metrics = (
            pd.DataFrame(metrics, columns=metrics.keys())
            .drop_duplicates(subset="id")
            .set_index("id")
        )
        return metrics

    def _train_test_split(self):
        x = self.metrics.copy()
        y = self.metrics["user_id"]
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)
        return x_train, x_test, y_train, y_test

    def calculate_cosine_similarity(self):
        matrix_dummy = self.full_matrix.copy().fillna(0)
        user_similarity = cosine_similarity(matrix_dummy)
        user_similarity = pd.DataFrame(
            user_similarity,
            index=self.full_matrix.index,
            columns=self.full_matrix.index,
        )
        return user_similarity

    # 정확도(RMSE)를 계산하는 함수
    def RMSE(self, y_true, y_pred):
        return np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2))

    def score(self, model):
        id_pairs = zip(self.x_test["user_id"], self.x_test["content_id"])
        y_pred = np.array([model(user, movie) for (user, movie) in id_pairs])
        y_true = np.array(self.x_test["metric_score"])
        return self.RMSE(y_true, y_pred)

    # 주어진 컨텐츠의 (content_id) 가중평균 rating을 계산하는 함수,
    # 가중치는 주어진 사용자와 다른 사용자 간의 유사도(user_similarity)
    def CF_simple(self, user_id, content_id):
        if content_id in self.full_matrix:
            # 현재 사용자와 다른 사용자 간의 similarity 가져오기
            sim_scores = self.user_cosine_similarity[user_id].copy()
            # 현재 컨텐츠에 대한 모든 사용자의 rating값 가져오기
            content_rating = self.full_matrix[content_id].copy()
            # 현재 컨텐츠를 평가하지 않은 사용자의 index 가져오기
            none_rating_idx = content_rating[content_rating.isnull()].index
            # 현재 컨텐츠를 평가하지 않은 사용자의 rating (null) 제거
            content_rating = content_rating.dropna()
            # 현재 컨텐츠를 평가하지 않은 사용자의 similarity값 제거
            sim_scores = sim_scores.drop(none_rating_idx)
            # 현재 컨텐츠를 평가한 모든 사용자의 가중평균값 구하기
            mean_rating = np.dot(sim_scores, content_rating) / sim_scores.sum()
        else:
            mean_rating = 3.0
        return mean_rating

    ##### (1)

    # Neighbor size를 정해서 예측치를 계산하는 함수
    def cf_knn(self, user_id, movie_id, neighbor_size=2):
        if movie_id in self.full_matrix:
            # 현재 사용자와 다른 사용자 간의 similarity 가져오기
            sim_scores = self.user_cosine_similarity[user_id].copy()
            # 현재 영화에 대한 모든 사용자의 rating값 가져오기
            movie_ratings = self.full_matrix[movie_id].copy()
            # 현재 영화를 평가하지 않은 사용자의 index 가져오기
            none_rating_idx = movie_ratings[movie_ratings.isnull()].index
            # 현재 영화를 평가하지 않은 사용자의 rating (null) 제거
            movie_ratings = movie_ratings.drop(none_rating_idx)
            # 현재 영화를 평가하지 않은 사용자의 similarity값 제거
            sim_scores = sim_scores.drop(none_rating_idx)
            ##### (2) Neighbor size가 지정되지 않은 경우
            if neighbor_size == 0:
                # 현재 영화를 평가한 모든 사용자의 가중평균값 구하기
                mean_rating = np.dot(sim_scores, movie_ratings) / sim_scores.sum()
            ##### (3) Neighbor size가 지정된 경우
            else:
                # 해당 영화를 평가한 사용자가 최소 2명이 되는 경우에만 계산
                if len(sim_scores) > 1:
                    # 지정된 neighbor size 값과 해당 영화를 평가한 총사용자 수 중 작은 것으로 결정
                    neighbor_size = min(neighbor_size, len(sim_scores))
                    # array로 바꾸기 (argsort를 사용하기 위함)
                    sim_scores = np.array(sim_scores)
                    movie_ratings = np.array(movie_ratings)
                    # 유사도를 순서대로 정렬
                    user_idx = np.argsort(sim_scores)
                    # 유사도를 neighbor size만큼 받기
                    sim_scores = sim_scores[user_idx][-neighbor_size:]
                    # 영화 rating을 neighbor size만큼 받기
                    movie_ratings = movie_ratings[user_idx][-neighbor_size:]
                    # 최종 예측값 계산
                    mean_rating = np.dot(sim_scores, movie_ratings) / sim_scores.sum()
                else:
                    mean_rating = 3.0
        else:
            mean_rating = 5.0
        return mean_rating

    def cf_knn_recommender(self, user, n_items=2, neighbor_size=2):
        """Recommend n_items for a given user based on collaborative filtering model."""
        # Calculate predicted ratings for all items for the current user
        predictions = []
        rated_index = self.full_matrix.loc[user][
            self.full_matrix.loc[user] > 0
        ].index  # Check already rated items
        items = self.full_matrix.loc[user].drop(
            rated_index
        )  # Items not yet rated by the user
        # print("items:", items)
        for item in items.index:
            predictions.append(
                self.cf_knn(user, item, neighbor_size)
            )  # Calculate predicted rating using cf_knn
        # print(predictions)
        recommendations = pd.Series(data=predictions, index=items.index, dtype=float)
        recommendations = recommendations.sort_values(ascending=False)[
            :n_items
        ]  # Select items with the highest predicted ratings

        # Get the recommended item indices
        recommended_items = recommendations.index

        # Filter out items that the user has already rated
        recommended_items = recommended_items[~recommended_items.isin(rated_index)]

        return recommended_items


if __name__ == "__main__":
    cf = CollaborativeFiltering()
    print("CF simple:", cf.score(cf.CF_simple))
    print("CF KNN:", cf.score(cf.cf_knn))
    print(cf.cf_knn_recommender(1))
