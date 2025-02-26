from src.db_handler import db_handler


def get_bills(bill_ids: list):
    result = []
    for id in bill_ids:
        result.append(db_handler.get_bill(id))
    return result


if __name__ == "__main__":
    bill_ids = [
        "PRC_V2R5L0V1K0Q8G1O3V4I4B0J2X0G1P6",
        "PRC_D2A5C0V1A0G9Y1S1C3J7I1T6Z3C4M9",
    ]
    results = get_bills(bill_ids)
    for i in results:
        print(i.title)
        print(i.body)
        print(i.url)
