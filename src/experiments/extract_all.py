from src.extractors import ConfExtractor, BillExtractor
from src.summary import Summarizer
from src.load import api_keyManager
from src.dna_logger import logger
import datetime
import time


def generate_date_list(start_date_str, end_date_str):
    # 문자열을 datetime.date 객체로 변환
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()

    date_list = []
    current_date = start_date

    # start_date부터 end_date까지 하루씩 증가시키면서 리스트에 추가
    while current_date <= end_date:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += datetime.timedelta(days=1)

    return date_list


def main(dae_num, date):
    conf = ConfExtractor(dae_num, date)
    print(conf.conf_info)
    if len(conf.conf_ids) == 0:
        logger.info("info: No Conf on this date")
        return
    conf.save_conf("localhost", "root", api_keyManager.get_db_password())
    print("conf.links: ", conf.links)
    for link in conf.links:
        print("link: ", link)
        bill = BillExtractor(link)
        print("bill.bill_info: ", bill.bill_info)
        # bill.save_bill("localhost", "root", api_keyManager.get_db_password())
        # su = Summarizer(bill.bill_summary)
        # su.bill_id = bill.get_bill_id()
        # su.conf_id = conf.get_conf_id()
        # if not su.bill_summary == "":
        #     su.save_summary("localhost", "root", api_keyManager.get_db_password())
        #     time.sleep(8)


if __name__ == "__main__":
    for date in generate_date_list("2024-06-01", "2025-03-9"):
        main("22", date)
