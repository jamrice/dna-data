from src.extractors import BillExtractor
from src.summary import Summarizer

be = BillExtractor(
    "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_U2Y3E0F8G0A9G1U0G0N9R0R0M1F0U0"
)
summarizer = Summarizer(be.bill_summary)
print("Headline : ", summarizer.get_headline())
print("Paragraph : ", summarizer.get_paragraph())