import numpy as np
import pandas as pd
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
        self.sig_level, self.min_ratings = self.set_sig_level_min_ratings()

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
        y_pred = np.array([model(user, content) for (user, content) in id_pairs])
        y_true = np.array(self.x_test["metric_score"])
        return self.RMSE(y_true, y_pred)

    # 주어진 컨텐츠의 (content_id) 가중평균 rating을 계산하는 함수,
    # 가중치는 주어진 사용자와 다른 사용자 간의 유사도(user_similarity)
    def cf_simple(self, user_id: int, content_id: str):
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
            if sim_scores.sum() != 0:  # Check to avoid division by zero
                mean_rating = np.dot(sim_scores, content_rating) / sim_scores.sum()
            else:
                mean_rating = 5.0  # Default value if no valid similarity scores
        else:
            mean_rating = 5.0
        return mean_rating

    # Neighbor size를 정해서 예측치를 계산하는 함수
    def cf_knn(self, user_id: int, content_id: str, neighbor_size=2):
        if content_id in self.full_matrix:
            # 현재 사용자와 다른 사용자 간의 similarity 가져오기
            sim_scores = self.user_cosine_similarity[user_id].copy()
            # 현재 컨텐츠에 대한 모든 사용자의 rating값 가져오기
            content_ratings = self.full_matrix[content_id].copy()
            # 현재 컨텐츠를 평가하지 않은 사용자의 index 가져오기
            none_rating_idx = content_ratings[content_ratings.isnull()].index
            # 현재 컨텐츠를 평가하지 않은 사용자의 rating (null) 제거
            content_ratings = content_ratings.drop(none_rating_idx)
            # 현재 컨텐츠를 평가하지 않은 사용자의 similarity값 제거
            sim_scores = sim_scores.drop(none_rating_idx)
            ##### Neighbor size가 지정되지 않은 경우
            if neighbor_size == 0:
                # 현재 컨텐츠를 평가한 모든 사용자의 가중평균값 구하기
                mean_rating = np.dot(sim_scores, content_ratings) / sim_scores.sum()
            ##### Neighbor size가 지정된 경우
            else:
                # 해당 컨텐츠를 평가한 사용자가 최소 2명이 되는 경우에만 계산
                if len(sim_scores) > 1:
                    # 지정된 neighbor size 값과 해당 컨텐츠를 평가한 총사용자 수 중 작은 것으로 결정
                    neighbor_size = min(neighbor_size, len(sim_scores))
                    # array로 바꾸기 (argsort를 사용하기 위함)
                    sim_scores = np.array(sim_scores)
                    content_ratings = np.array(content_ratings)
                    # 유사도를 순서대로 정렬
                    user_idx = np.argsort(sim_scores)
                    # 유사도를 neighbor size만큼 받기
                    sim_scores = sim_scores[user_idx][-neighbor_size:]
                    # 컨텐츠 rating을 neighbor size만큼 받기
                    content_ratings = content_ratings[user_idx][-neighbor_size:]
                    # 최종 예측값 계산
                    mean_rating = np.dot(sim_scores, content_ratings) / sim_scores.sum()
                else:
                    mean_rating = 5.0
        else:
            mean_rating = 5.0
        return mean_rating

    def cf_knn_bias(self, user_id: int, content_id: str, neighbor_size=0):
        # train 데이터의 user의 rating 평균과 컨텐츠의 평점편차 계산
        rating_mean = self.full_matrix.mean(axis=1)
        rating_bias = (self.full_matrix.T - rating_mean).T
        if content_id in rating_bias:
            # 현 user와 다른 사용자 간의 유사도 가져오기
            sim_scores = self.user_cosine_similarity[user_id].copy()
            # 현 content의 평점편차 가져오기
            content_ratings = rating_bias[content_id].copy()
            # 현 content에 대한 rating이 없는 사용자 삭제
            none_rating_idx = content_ratings[content_ratings.isnull()].index
            content_ratings = content_ratings.drop(none_rating_idx)
            sim_scores = sim_scores.drop(none_rating_idx)
            ##### (2) Neighbor size가 지정되지 않은 경우
            if neighbor_size == 0:
                # 편차로 예측값(편차 예측값) 계산
                prediction = np.dot(sim_scores, content_ratings) / sim_scores.sum()
                # 편차 예측값에 현 사용자의 평균 더하기
                prediction = prediction + rating_mean[user_id]
            ##### (3) Neighbor size가 지정된 경우
            else:
                # 해당 컨텐츠를 평가한 사용자가 최소 2명이 되는 경우에만 계산
                if len(sim_scores) > 1:
                    # 지정된 neighbor size 값과 해당 컨텐츠를 평가한 총사용자 수 중 작은 것으로 결정
                    neighbor_size = min(neighbor_size, len(sim_scores))
                    # array로 바꾸기 (argsort를 사용하기 위함)
                    sim_scores = np.array(sim_scores)
                    content_ratings = np.array(content_ratings)
                    # 유사도를 순서대로 정렬
                    user_idx = np.argsort(sim_scores)
                    # 유사도와 rating을 neighbor size만큼 받기
                    sim_scores = sim_scores[user_idx][-neighbor_size:]
                    content_ratings = content_ratings[user_idx][-neighbor_size:]
                    # 편차로 예측치 계산
                    prediction = np.dot(sim_scores, content_ratings) / sim_scores.sum()
                    # 예측값에 현 사용자의 평균 더하기
                    prediction = prediction + rating_mean[user_id]
                else:
                    prediction = rating_mean[user_id]
        else:
            prediction = rating_mean[user_id]
        return prediction

    def set_sig_level_min_ratings(self, sig_level: int = 3, min_ratings: int = 2):
        return sig_level, min_ratings

    def cf_knn_bias_sig(self, user_id: int, content_id: str, neighbor_size=0):
        # train 데이터의 user의 rating 평균과 컨텐츠의 평점편차 계산
        rating_mean = self.full_matrix.mean(axis=1)
        rating_bias = (self.full_matrix.T - rating_mean).T

        # 사용자별 공통 평가 수 계산
        rating_binary1 = np.array((self.full_matrix > 0).astype(float))
        rating_binary2 = rating_binary1.T
        counts = np.dot(rating_binary1, rating_binary2)
        counts = pd.DataFrame(
            counts, index=self.full_matrix.index, columns=self.full_matrix.index
        ).fillna(0)

        if content_id in rating_bias:
            # 현 user와 다른 사용자 간의 유사도 가져오기
            sim_scores = self.user_cosine_similarity[user_id]
            # 현 content의 평점편차 가져오기
            content_ratings = rating_bias[content_id]
            # 현 content에 대한 rating이 없는 사용자 표시
            no_rating = content_ratings.isnull()
            # 현 사용자와 다른 사용자간 공통 평가 아이템 수 가져오기
            common_counts = counts[user_id]
            # 공통으로 평가한 컨텐츠의 수가 SIG_LEVEL보다 낮은 사용자 표시
            low_significance = common_counts < self.sig_level
            # 평가를 안 하였거나, SIG_LEVEL이 기준 이하인 user 제거
            none_rating_idx = content_ratings[no_rating | low_significance].index
            content_ratings = content_ratings.drop(none_rating_idx)
            sim_scores = sim_scores.drop(none_rating_idx)
            ##### (2) Neighbor size가 지정되지 않은 경우
            if neighbor_size == 0:
                # 편차로 예측값(편차 예측값) 계산
                prediction = np.dot(sim_scores, content_ratings) / sim_scores.sum()
                # 편차 예측값에 현 사용자의 평균 더하기
                prediction = prediction + rating_mean[user_id]
            ##### (3) Neighbor size가 지정된 경우
            else:
                # 해당 컨텐츠를 평가한 사용자가 최소 MIN_RATINGS 이상인 경우에만 계산
                if len(sim_scores) > self.min_ratings:
                    # 지정된 neighbor size 값과 해당 컨텐츠를 평가한 총사용자 수 중 작은 것으로 결정
                    neighbor_size = min(neighbor_size, len(sim_scores))
                    # array로 바꾸기 (argsort를 사용하기 위함)
                    sim_scores = np.array(sim_scores)
                    content_ratings = np.array(content_ratings)
                    # 유사도를 순서대로 정렬
                    user_idx = np.argsort(sim_scores)
                    # 유사도와 rating을 neighbor size만큼 받기
                    sim_scores = sim_scores[user_idx][-neighbor_size:]
                    content_ratings = content_ratings[user_idx][-neighbor_size:]
                    # 편차로 예측치 계산
                    prediction = np.dot(sim_scores, content_ratings) / sim_scores.sum()
                    # 예측값에 현 사용자의 평균 더하기
                    prediction = prediction + rating_mean[user_id]
                else:
                    prediction = rating_mean[user_id]
        else:
            prediction = rating_mean[user_id]
        return prediction

    def recommender(
        self, model, user_id: int, n_items: int = 20, neighbor_size: int = 5
    ):
        """Recommend n_items for a given user based on collaborative filtering model."""
        # Calculate predicted ratings for all items for the current user
        predictions = []
        rated_index = self.full_matrix.loc[user_id][
            self.full_matrix.loc[user_id] > 0
        ].index  # Check already rated items
        items = self.full_matrix.loc[user_id].drop(
            rated_index
        )  # Items not yet rated by the user
        # print("items:", items)
        for item in items.index:
            predictions.append(
                model(user_id, item, neighbor_size)
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
    print("CF simple:", cf.score(cf.cf_simple))
    print("CF KNN:", cf.score(cf.cf_knn))
    print("CF KNN user bias:", cf.score(cf.cf_knn_bias))
    print("CF KNN bias sig:", cf.score(cf.cf_knn_bias_sig))
    print(cf.recommender(cf.cf_knn, 0))
    print(cf.recommender(cf.cf_knn_bias, 0))
    print(cf.recommender(cf.cf_knn_bias_sig, 0))
