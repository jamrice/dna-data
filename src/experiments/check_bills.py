from src.db_handler import db_handler


def get_bills(bill_ids: list):
    result = []
    for id in bill_ids:
        result.append(db_handler.get_bill(id))
    return result


if __name__ == "__main__":
    bill_ids = [
        "PRC_K2G5H0F2F1D3C1D0K1L1K0K3J5H5I4",
        "PRC_P2O4N0O6J0I3H1F1O2P4N2M6S0R6Z6",
    ]
    results = get_bills(bill_ids)
    for i in results:
        print(i.title)
        print(i.body)
        print(i.url)
