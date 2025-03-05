from src.dna_logger import logger
from src.summary import Summarizer
from src.db_handler import get_db_handler

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityScoreGenerator:

    def __init__(self):
        self.db_handler = get_db_handler()
        self.contents = []
        self.translated_contents = []

    def get_contents(self):
        contents = self.db_handler.get_bills_content()
        self.contents = [content for content in contents if content is not None]
        return self.contents

    def translate_content(self):
        try:
            if not self.contents:
                logger.warning("No bills found in database")
                return

            translated_contents = []

            for bill in self.contents:
                # Check if translations already exist in the database
                existing_translation = self.db_handler.get_existing_translation(
                    bill["bill_id"]
                )
                if existing_translation:
                    translated_contents.append(existing_translation)
                    logger.info(
                        f"Skipped translation for bill {bill['bill_id']}, already exists."
                    )
                    continue  # Skip to the next bill if translation exists

                success = False
                attempts = 0
                while not success and attempts < 3:  # Retry up to 3 times
                    try:
                        summarizer = Summarizer(bill["bill_summary"])
                        translated_summary = summarizer.translate_to_english(
                            bill["bill_summary"]
                        )
                        translated_title = summarizer.translate_to_english(
                            bill["bill_title"]
                        )

                        if translated_summary is not None:
                            translated_contents.append(
                                {
                                    "id": bill["bill_id"],
                                    "translated_bill_title": translated_title,
                                    "translated_bill_summary": translated_summary,
                                }
                            )
                            # Save to bills model
                            self.db_handler.save_bill_translation(
                                bill["bill_id"], translated_title, translated_summary
                            )
                            logger.info(
                                f"Translated content for bill {bill['bill_id']}: \n {translated_title} \n {translated_summary}"
                            )
                            success = True
                        else:
                            translated_contents.append(
                                {
                                    "id": bill["bill_id"],
                                    "translated_bill_title": translated_title,
                                    "translated_bill_summary": translated_title,
                                }
                            )
                            logger.warning(
                                f"Attempt {attempts+1}: Translation failed for bill {bill['bill_id']}"
                            )
                            attempts += 1  # Increment attempts on failure
                    except Exception as e:
                        logger.error(
                            f"Attempt {attempts+1}: Error during translation for bill {bill['bill_id']}: {str(e)}"
                        )
                        attempts += 1  # Increment attempts on exception

            if not translated_contents:
                logger.warning("No valid translated contents found.")
                return

            self.translated_contents = translated_contents
            return self.translated_contents

        except Exception as e:
            logger.error(f"Error in translate_content process: {str(e)}")
            raise

    def generate_summary_similarity_score(self):
        """summary에 대한 similarity score 생성"""
        try:
            # Filter out bills where translated_bill_title equals translated_bill_summary
            valid_bills = [
                bill
                for bill in self.translated_contents
                if bill["translated_bill_title"] != bill["translated_bill_summary"]
            ]
            # Log if no valid bills are found
            if not valid_bills:
                logger.warning("No valid bills found for similarity score calculation.")
                return None  # Return None if no valid bills

            # TF-IDF 벡터라이저 설정
            tfidf_vectorizer = TfidfVectorizer(stop_words="english")
            # bill_title과 bill_summary의 내용으로 코사인 유사도 추출
            # 이후에 다른 내용이 추가될 수 있음
            tfidf_matrix = tfidf_vectorizer.fit_transform(
                [
                    bill["translated_bill_title"]
                    + " "
                    + bill["translated_bill_summary"]
                    for bill in valid_bills
                ]
            )

            # 코사인 유사도 계산
            cosine_sim = cosine_similarity(tfidf_matrix)
            cosine_sim_df = pd.DataFrame(cosine_sim)

            # 추천 결과 생성 및 DB에 저장
            for idx, bill in enumerate(valid_bills):
                source_bill_id = bill["id"]  # 현재 법안의 ID를 source_bill_id로 설정
                for sim_idx in range(len(valid_bills)):  # 모든 법안에 대해 반복
                    if sim_idx != idx:  # 자기 자신 제외
                        target_bill_id = valid_bills[sim_idx]["id"]
                        similarity_score = cosine_sim[idx][sim_idx]
                        self.db_handler.save_similarity_score(
                            target_bill_id, source_bill_id, similarity_score
                        )

            return cosine_sim_df

        except Exception as e:
            logger.error(f"Error in recommendation generation process: {str(e)}")
            raise

    # this function is deprecated the recommendation algorithm above will take into account all features available
    def generate_others_similarity_score(self):
        """summary 제외 내용들에 대한 similarity score 생성"""
        try:
            # TF-IDF 벡터라이저 설정
            tfidf_vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = tfidf_vectorizer.fit_transform(
                [bill["translated_bill_title"] for bill in self.translated_contents]
            )

            # 코사인 유사도 계산
            cosine_sim = cosine_similarity(tfidf_matrix)
            cosine_sim_df = pd.DataFrame(cosine_sim)

            # 추천 결과 생성 및 DB에 저장
            for idx, bill in enumerate(self.translated_contents):
                source_bill_id = bill["id"]  # 현재 법안의 ID를 source_bill_id로 설정
                for sim_idx in range(
                    len(self.translated_contents)
                ):  # 모든 법안에 대해 반복
                    if sim_idx != idx:  # 자기 자신 제외
                        target_bill_id = self.translated_contents[sim_idx]["id"]
                        similarity_score = cosine_sim[idx][sim_idx]
                        self.db_handler.save_similarity_score(
                            target_bill_id, source_bill_id, similarity_score
                        )

            return cosine_sim_df

        except Exception as e:
            logger.error(f"Error in recommendation generation process: {str(e)}")
            raise


if __name__ == "__main__":
    ssg = SimilarityScoreGenerator()
    contents = ssg.get_contents()
    print("contents: ", contents)
    t_contents = ssg.translate_content()
    print("t_contents: ", t_contents)
    summary_cosine_sim_df = ssg.generate_summary_similarity_score()
    print("summary df:\n", summary_cosine_sim_df)
