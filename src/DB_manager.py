import mysql.connector
from src.load import api_keyManager
from src.dna_logger import logger

def catch_sql_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except mysql.connector.Error as err:
            logger.error(f"error: mysql error occurred {err}")

    return wrapper


class DB_manager:

    def __init__(self, host, user, password):
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, password=password, database="test_db"
            )
            self.cursor = self.connection.cursor()
            return

        except mysql.connector.Error as err:
            logger.error(f"error: mysql error occurred {err}")

    # def __del__(self):
    #     if self.cursor:
    #         self.cursor.close()
    #     if self.connection:
    #         self.connection.close()
    def save_bill(self, params):
        table = "bill"
        columns = [
            "bill_id",
            "url",
            "num",
            "title",
            "body",
            "pdf_url",
            "date",
            "ord_num",
        ]
        self.save_table(table, columns, params)
        return

    def del_bill(self, bill_id):
        table = "bill"
        column = "bill_id"
        self.del_table(table, column, bill_id)

    def save_conf(self, params):
        table = "bill"
        columns = [
            "bill_id",
            "url",
            "num",
            "title",
            "body",
            "pdf_url",
            "date",
            "ord_num",
        ]
        self.save_table(table, columns, params)

    @catch_sql_except
    def save_table(self, table, columns, params):
        columns_text = ", ".join(columns)
        logger.debug(columns_text)
        ss = [f"%s"] * len(columns)
        s_text = ", ".join(ss)
        logger.debug(s_text)
        sql = f"INSERT INTO {table} ({columns_text}) VALUES ({s_text})"
        logger.debug(sql)
        self.cursor.execute(sql, params)
        self.connection.commit()

    @catch_sql_except
    def del_table(self, table, column, value):
        sql = f"DELETE FROM {table} WHERE {column} = %s"
        logger.debug(sql)
        self.cursor.execute(sql, [value])
        self.connection.commit()

    @catch_sql_except
    def read_all_value_table(self, table, column):
        query = f"""SELECT {column}
                    FROM {table};"""
        # 쿼리 실행
        self.cursor.execute(query)
        logger.debug("excute query:" + query)
        # 데이터 가져오기
        results = self.cursor.fetchall()
        logger.debug("Findings number:" + str(len(results)))
        return results

    @catch_sql_except
    def read_value_table(self, table, column, value):

        query = f"""SELECT * 
                    FROM {table} 
                    WHERE {column} = %s;"""
        # 쿼리 실행
        self.cursor.execute(query, [value])

        # 데이터 가져오기
        results = self.cursor.fetchall()
        return results[0]

    @catch_sql_except
    def update_value(self, table, column, value, set_column, set_value):

        query = f"""UPDATE {table}  
                SET  {set_column} = %s
                WHERE {column} = %s;"""

        self.cursor.execute(query, [set_value, value])
        self.connection.commit()


# id pw for tomato's local db
db_manager = DB_manager("localhost", "root", api_keyManager.get_db_password())

if __name__ == "__main__":
    params = [
        "test_id",
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_N2C4C1O1V2V0N2G0J5X0V5Z3L7Z5Z0",
        "11111111",
        "테스트 헤드라인",
        "테스트 요약",
        "https://likms.assembly.go.kr/filegate/sender24?dummy=dummy&bookId=8A944004-E8FF-C5BE-948F-304B7A8B1790&type=1",
        "2024-11-27",
        "22",
    ]
    db_manager.save_bill(params)
    db_manager.del_bill("test_id")
