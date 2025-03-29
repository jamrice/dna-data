from src.extractors import ConfExtractor, BillExtractor
from src.summary import Summarizer
from src.load import api_keyManager
from src.dna_logger import logger
import datetime
import time
# 국회 대수별 시작일자 정보를 저장
assembly_dates = [
    (1, "1948-05-31"),
    (2, "1950-05-31"), 
    (3, "1954-05-31"),
    (4, "1958-05-30"),
    (5, "1960-07-29"),
    (6, "1963-12-17"),
    (7, "1967-06-06"),
    (8, "1971-07-01"), 
    (9, "1973-03-12"),
    (10, "1979-03-12"),
    (11, "1981-04-11"),
    (12, "1985-04-11"),
    (13, "1988-05-30"),
    (14, "1992-05-30"),
    (15, "1996-05-30"),
    (16, "2000-05-30"),
    (17, "2004-05-30"),
    (18, "2008-05-30"),
    (19, "2012-05-30"),
    (20, "2016-05-30"),
    (21, "2020-05-30"),
    (22, "2024-05-30")
]

def get_assembly_number(date_str) -> str:
    """주어진 날짜에 해당하는 국회 대수를 반환합니다.
    
    Args:
        date_str: YYYY-MM-DD 형식의 날짜 문자열
        
    Returns:
        해당 날짜의 국회 대수(정수). 해당하는 대수가 없으면 None 반환
    """
    target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    
    for i in range(len(assembly_dates)-1):
        start = datetime.datetime.strptime(assembly_dates[i][1], "%Y-%m-%d").date()
        end = datetime.datetime.strptime(assembly_dates[i+1][1], "%Y-%m-%d").date()
        if start <= target_date < end:
            return assembly_dates[i][0]
            
    # 마지막 대수 처리
    last_start = datetime.datetime.strptime(assembly_dates[-1][1], "%Y-%m-%d").date()
    if target_date >= last_start:
        return assembly_dates[-1][0]
        
    return None

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
    for date in generate_date_list("2025-01-01", "2025-01-31"):
        main(get_assembly_number(date), date)
