from src.summary import Summarizer
from src.db_handler import get_db_handler
from src.extractors import BillExtractor


if __name__ == "__main__":
    be = BillExtractor(
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_U2Y3E0F8G0A9G1U0G0N9R0R0M1F0U0"
    )
    sz = Summarizer(be.bill_summary)
    sz.bill_id = be.bill_info["bill_id"]
    print("Headline : ", sz.get_headline())
    print("Paragraph : ", sz.get_paragraph())
    db_handler = get_db_handler()
    sm = db_handler.save_summary(sz)
    print("done")
