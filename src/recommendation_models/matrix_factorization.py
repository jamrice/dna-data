import numpy as np
import pandas as pd
from src.dna_logger import logger
from src.db_handler import get_db_handler
from sqlalchemy import text

from sklearn.utils import shuffle


class MatrixFactorization:
    def __init__(self, K, alpha, beta, iterations, verbose=True):
        self.db_handler = get_db_handler()
        self.metrics = self.get_metrics()

        # Extract unique user and content IDs
        self.user_ids = self.metrics["user_id"].unique()
        self.content_ids = self.metrics["content_id"].unique()

        # Create mappings between actual IDs and continuous indices
        self.user_id_index = {user_id: i for i, user_id in enumerate(self.user_ids)}
        self.content_id_index = {
            content_id: i for i, content_id in enumerate(self.content_ids)
        }

        # Prepare matrix based on user and content mappings
        self.num_users = len(self.user_ids)
        self.num_contents = len(self.content_ids)
        self.matrix = np.zeros(
            (self.num_users, self.num_contents)
        )  # Initialize empty matrix

        # Fill in the matrix with the metric_score values
        for _, row in self.metrics.iterrows():
            user_index = self.user_id_index[row["user_id"]]
            content_index = self.content_id_index[row["content_id"]]
            self.matrix[user_index, content_index] = row[
                "metric_score"
            ]  # Fill with metric_score
        # self.num_users, self.num_contents = np.shape(self.R)
        self.R = self.matrix
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iterations = iterations
        self.verbose = verbose

    def get_metrics(self):
        metrics = self.db_handler.db.execute(text("SELECT * FROM user_content_metrics"))
        metrics = (
            pd.DataFrame(metrics, columns=metrics.keys())
            .drop_duplicates(subset="id")
            .set_index("id")
        )
        return metrics

    # train set의 RMSE 계산
    def rmse(self):
        xs, ys = self.R.nonzero()
        self.predictions = []
        self.errors = []
        for x, y in zip(xs, ys):
            prediction = self.get_prediction(x, y)
            self.predictions.append(prediction)
            self.errors.append(self.R[x, y] - prediction)
        self.predictions = np.array(self.predictions)
        self.errors = np.array(self.errors)
        return np.sqrt(np.mean(self.errors**2))

    # metrics for user i and content j
    def get_prediction(self, i, j):
        prediction = (
            self.b + self.b_u[i] + self.b_d[j] + self.P[i, :].dot(self.Q[j, :].T)
        )
        return prediction

    # Stochastic gradient descent to get optimized P and Q matrix
    def sgd(self):
        for i, j, r in self.samples:
            prediction = self.get_prediction(i, j)
            e = r - prediction

            self.b_u[i] += self.alpha * (e - self.beta * self.b_u[i])
            self.b_d[j] += self.alpha * (e - self.beta * self.b_d[j])

            self.P[i, :] += self.alpha * (e * self.Q[j, :] - self.beta * self.P[i, :])
            self.Q[j, :] += self.alpha * (e * self.P[i, :] - self.beta * self.Q[j, :])

    # Test set을 선정
    def set_test(self, metrics_test):
        """Prepare test set with actual IDs mapped to indices."""
        test_set = []
        for i in range(len(metrics_test)):
            user_id = metrics_test.iloc[i, 0]
            content_id = metrics_test.iloc[i, 1]
            metric = metrics_test.iloc[i, 2]  # Extract the metric value

            # Safely map IDs to indices
            if user_id in self.user_id_index and content_id in self.content_id_index:
                user_index = self.user_id_index[user_id]
                content_index = self.content_id_index[content_id]
                test_set.append((user_index, content_index, metric))

                self.R[user_index, content_index] = 0
            else:
                print(
                    f"Skipping missing user_id: {user_id} or content_id: {content_id}"
                )
        self.test_set = test_set
        return test_set

    # Test set의 RMSE 계산
    def test_rmse(self):
        error = 0
        for one_set in self.test_set:
            predicted = self.get_prediction(one_set[0], one_set[1])
            error += pow(one_set[2] - predicted, 2)
        return np.sqrt(error / len(self.test_set))

    # Training 하면서 test set의 정확도를 계산
    def test(self):
        # Initializing user-feature and content-feature matrix
        self.P = np.random.normal(scale=1.0 / self.K, size=(self.num_users, self.K))
        self.Q = np.random.normal(scale=1.0 / self.K, size=(self.num_contents, self.K))

        # Initializing the bias terms
        self.b_u = np.zeros(self.num_users)
        self.b_d = np.zeros(self.num_contents)
        self.b = np.mean(self.R[self.R.nonzero()])

        # List of training samples
        rows, columns = self.R.nonzero()
        self.samples = [(i, j, self.R[i, j]) for i, j in zip(rows, columns)]

        # Stochastic gradient descent for given number of iterations
        training_process = []
        for i in range(self.iterations):
            np.random.shuffle(self.samples)
            self.sgd()
            rmse1 = self.rmse()
            rmse2 = self.test_rmse()
            training_process.append((i + 1, rmse1, rmse2))
            if self.verbose:
                if (i + 1) % 10 == 0:
                    print(
                        "Iteration: %d ; Train RMSE = %.4f ; Test RMSE = %.4f"
                        % (i + 1, rmse1, rmse2)
                    )
        return training_process

    # metrics for given user_id and content_id
    def get_one_prediction(self, user_id, content_id):
        """Predict score for one (user_id, content_id) pair."""
        if user_id in self.user_id_index and content_id in self.content_id_index:
            user_index = self.user_id_index[user_id]
            content_index = self.content_id_index[content_id]
            return self.get_prediction(user_index, content_index)
        else:
            return None  # Return None if the ID is not found

    # Full user-content rating matrix
    # need to add bias for actual values
    def full_prediction(self):
        return (
            self.b
            + self.b_u[:, np.newaxis]
            + self.b_d[np.newaxis, :]
            + self.P.dot(self.Q.T)
        )


if __name__ == "__main__":

    # # Testing MF RMSE
    mf = MatrixFactorization(
        K=160, alpha=0.001, beta=0.02, iterations=288, verbose=True
    )
    # TRAIN_SIZE = 0.75
    # metrics = shuffle(mf.metrics, random_state=1)
    # cutoff = int(TRAIN_SIZE * len(metrics))
    # metrics_train = metrics.iloc[:cutoff]
    # metrics_test = metrics.iloc[cutoff:]
    # test_set = mf.set_test(metrics_test)
    # result = mf.test()

    # # Printing predictions
    # print(mf.full_prediction()[1])
    # print(mf.get_one_prediction(0, "law_abolition_1"))

    TRAIN_SIZE = 0.75
    metrics = shuffle(mf.metrics, random_state=1)
    cutoff = int(TRAIN_SIZE * len(metrics))
    metrics_train = metrics.iloc[:cutoff]
    metrics_test = metrics.iloc[cutoff:]
    # 최적의 K값 찾기
    results = []
    index = []
    for K in range(50, 261, 10):
        print("K =", K)
        mf = MatrixFactorization(
            K=K, alpha=0.001, beta=0.02, iterations=500, verbose=True
        )

        test_set = mf.set_test(metrics_test)
        result = mf.test()
        index.append(K)
        results.append(result)

    # 최적의 iterations 값 찾기
    summary = []
    for i in range(len(results)):
        RMSE = []
        for result in results[i]:
            RMSE.append(result[2])
        min = np.min(RMSE)
        j = RMSE.index(min)
        summary.append([index[i], j + 1, RMSE[j]])

    print(summary)
