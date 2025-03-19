from src.extractors import BillExtractor
from src.dna_logger import logger

import os
from dotenv import load_dotenv


def save_bills_from_urls(
    bill_urls, host="localhost", user="root", password="your_password"
):
    """
    Extract bill information from given URLs and save them to the database.

    Parameters:
        bill_urls (list): List of bill URLs to process
        host (str): Database host address
        user (str): Database username
        password (str): Database password
    """

    total_bills = len(bill_urls)
    success_count = 0
    failed_urls = []

    for idx, url in enumerate(bill_urls, 1):
        try:
            logger.info(f"Processing bill {idx}/{total_bills}: {url}")

            # Extract bill information
            bill_extractor = BillExtractor(url)

            # Save to database
            bill_extractor.save_bill(host=host, user=user, password=password)

            success_count += 1
            logger.info(f"Successfully saved bill {bill_extractor.bill_no}")

        except Exception as e:
            logger.error(f"Failed to process URL {url}: {str(e)}")
            failed_urls.append(url)
            continue

    # Log summary
    logger.info(f"\nProcessing complete!")
    logger.info(f"Successfully processed: {success_count}/{total_bills} bills")

    if failed_urls:
        logger.warning(f"Failed URLs ({len(failed_urls)}):")
        for url in failed_urls:
            logger.warning(url)


if __name__ == "__main__":
    # Example usage
    test_urls = [
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_T2R5S0Q2R1Y3X1X4W4W5V5V7D7E2C2",
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_K2G5H0F2F1D3C1D0K1L1K0K3J5H5I4",
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_M2I4G0H8G2G1E1F6N1L6M0K7K1J5K4",
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_T2O4P1O2O2M7N1L5T5U0S5T1R2S1Q5",
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_X2V4W1U1V2D9D1C3A5B3Z5A3I3I4G8",
        # Add more URLs as needed
    ]

    # 환경변수를 사용하여 비밀번호 가져오기
    load_dotenv()
    DB_USER = os.getenv("DATABASE_USERNAME")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DB_HOST = "localhost"

    save_bills_from_urls(test_urls, host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
