from src.load import api_keyManager
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
import re
from src.dna_logger import logger
from src.db_handler import db_manager
import google.generativeai as genai


class ConfExtractor:
    """
    Extracts conference details from the National Assembly API using DAE_NUM and CONF_DATE.
    """

    def __init__(self, dae_num: str, date: str):
        """
        Initializes the ConfExtractor by fetching the first conference ID and its details
        from the National Assembly API based on the DAE_NUM and CONF_DATE.

        Parameters:
            dae_num (str): The National Assembly number (DAE_NUM).
            date (str): The date of the conference (CONF_DATE).
        """
        self.dae_num = dae_num
        self.date = date
        self.na_api_key = api_keyManager.get_na_api_key()
        self.conf_ids = []  # To store conference IDs
        self.links = []  # Store relevant links like VOD or PDF links
        self.conf_info = {}  # Store information about the first conference

        self.get_conf_info(dae_num, date)  # Fetch the first conference entry

        if self.conf_ids:
            self.get_link_from_conf_id(self.conf_ids[0])

    def get_conf_info(self, dae_num: str, date: str) -> tuple:
        """
        Retrieves the first conference ID and relevant details from the National Assembly API.

        Parameters:
            dae_num (str): The DAE_NUM to search for.
            date (str): The CONF_DATE to search for.

        Returns:
            tuple: A tuple containing a list of conference IDs and a list of conference details.
        """
        base_url = "https://open.assembly.go.kr/portal/openapi/nzbyfwhwaoanttzje"
        self.params_dict = {
            "KEY": self.na_api_key,
            "Type": "xml",  # Assuming you are receiving XML data
            "pSize": 1000,
            "DAE_NUM": dae_num,
            "CONF_DATE": date,
        }
        response = requests.get(base_url, params=self.params_dict)

        if response.status_code != 200:
            logger.error(
                f"Error: Failed to fetch data, status code {response.status_code}"
            )
            return None

        try:
            root = ET.fromstring(response.content)
            result_code = root.find(".//CODE").text
            if result_code != "INFO-000":
                logger.error(f"Error: {root.find('.//MESSAGE').text}")
                return None

            # Extract the first conference information
            row = root.find(".//row")
            if row is not None:
                conference = {
                    "CONFER_NUM": row.find("CONFER_NUM").text,
                    "TITLE": row.find("TITLE").text,
                    "CLASS_NAME": row.find("CLASS_NAME").text,
                    "CONF_DATE": row.find("CONF_DATE").text,
                    "VOD_LINK_URL": row.find("VOD_LINK_URL").text,
                    "CONF_LINK_URL": row.find("CONF_LINK_URL").text,
                    "PDF_LINK_URL": row.find("PDF_LINK_URL").text,
                }
                self.conf_info = conference
                self.conf_ids = [conference["CONFER_NUM"]]
                return self.conf_ids, self.conf_info

        except ET.ParseError as e:
            logger.error(f"Error: Failed to parse XML - {str(e)}")
            logger.error("Response content:", response.text)
            return None

    def get_conf_id(self):
        return self.conf_ids[0]

    def get_link_from_conf_id(self, conf_id: str):
        """
        Retrieves bill links associated with a specific conference ID from the National Assembly API.

        Parameters:
            conf_id (str): The conference ID to fetch the bill links for.

        Appends the bill links to the self.links list.
        """
        base_url = "https://open.assembly.go.kr/portal/openapi/VCONFBILLLIST"
        params_dict = {
            "KEY": self.na_api_key,
            "Type": "json",
            "pSize": 1000,
            "CONF_ID": conf_id,
        }
        response = requests.get(base_url, params=params_dict)

        if response.status_code == 200:
            try:
                for row in response.json()["VCONFBILLLIST"][1]["row"]:
                    self.links.append(row["LINK_URL"])
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                logger.error(f"conf_id: {conf_id}")
        else:
            logger.error(
                f"Error: Failed to retrieve links, status code {response.status_code}"
            )

    def save_conf(self, host, user, password):
        """
        Save to Database.

        Parameters:
            host (str): Database host ip ex) localhost.
            user (str): User name in database ex) root.
            password (str): Password for user.
        """

        params = (
            self.conf_ids[0],
            self.conf_info["CONF_LINK_URL"],
            self.conf_info["CONFER_NUM"],
            self.conf_info["TITLE"],
            self.conf_info["PDF_LINK_URL"],
            self.conf_info["CONF_DATE"],
            self.params_dict["DAE_NUM"],
        )

        db_manager.save_conf(params=params)


## ConfExtractor that takes into account for multiple conference for a day.
class MultiConfExtractor:
    def __init__(self, dae_num, date):
        self.na_api_key = self.api_km.get_na_api_key()
        self.conf_ids = None
        self.links = []
        self.conf_info = []
        self.get_conf_id_from_date(dae_num, date)
        if self.conf_ids:
            self.get_link_from_conf_id(self.conf_ids[0])

    def get_conf_id_from_date(self, dae_num, date):
        """
        Retrieves conference IDs and relevant details from the 열린국회 API based on the provided dae_num and date.

        Parameters:
        dae_num (str): The DAE_NUM to search for.
        date (str): The CONF_DATE to search for.

        Returns:
        list: A list of conference details including CONFER_NUM, TITLE, CLASS_NAME, CONF_DATE, VOD_LINK_URL, CONF_LINK_URL, and PDF_LINK_URL.
        """
        base_url = "https://open.assembly.go.kr/portal/openapi/nzbyfwhwaoanttzje"
        params_dict = {
            "KEY": self.na_api_key,
            "Type": "xml",  # Assuming you are receiving XML data
            "pSize": 1000,
            "DAE_NUM": dae_num,
            "CONF_DATE": date,
        }
        response = requests.get(base_url, params=params_dict)

        if response.status_code != 200:
            print(f"Error: Failed to fetch data, status code {response.status_code}")
            return None

        try:
            # Parse the XML response
            root = ET.fromstring(response.content)

            # Check for the result code
            result_code = root.find(".//CODE").text
            if result_code != "INFO-000":
                print(f"Error: {root.find('.//MESSAGE').text}")
                return None

            # Extract conference information
            ids = []
            for row in root.findall(".//row"):
                conference = {
                    "CONFER_NUM": row.find("CONFER_NUM").text,
                    "TITLE": row.find("TITLE").text,
                    "CLASS_NAME": row.find("CLASS_NAME").text,
                    "CONF_DATE": row.find("CONF_DATE").text,
                    "VOD_LINK_URL": row.find("VOD_LINK_URL").text,
                    "CONF_LINK_URL": row.find("CONF_LINK_URL").text,
                    "PDF_LINK_URL": row.find("PDF_LINK_URL").text,
                }
                ids.append(conference["CONFER_NUM"])
                self.conf_info.append(conference)

            self.conf_ids = list(set(ids))

        except ET.ParseError as e:
            print(f"Error: Failed to parse XML - {str(e)}")
            print("Response content:", response.text)
            return None

    def get_link_from_conf_id(self, CONF_ID):
        """
        Retrieves bill links associated with a specific conference ID.

        Parameters:
        CONF_ID (str): The conference ID to fetch the bill links for.

        Appends the bill links to the self.links list.
        """
        # base_url (기본 URL)
        base_url = "https://open.assembly.go.kr/portal/openapi/VCONFBILLLIST"
        params_dict = {
            "KEY": self.na_api_key,
            "Type": "json",
            "pSize": 1000,
            "CONF_ID": CONF_ID,
        }
        response = requests.get(base_url, params=params_dict)

        if response.status_code == 200:
            for row in response.json()["VCONFBILLLIST"][1]["row"]:
                self.links.append(row["LINK_URL"])
        else:
            print("GET 요청 실패:", response.status_code)


class BillExtractor:
    """
    Extracts bill information and details from the National Assembly API and bill web pages.
    """

    def __init__(self, bill_url: str):
        """
        Initializes the BillExtractor class by setting up attributes for bill-related data.

        Parameters:
            bill_url (str): The URL of the bill's webpage.
        """
        self.na_api_key = api_keyManager.get_na_api_key()
        self.bill_url = bill_url
        self.bill_soup = self.get_soup(self.bill_url)
        self.bill_summary = self.get_bill_summary()
        self.bill_no, self.pdf_url = self.get_bill_no_pdf_url()
        self.bill_info = self.get_bill_info(self.bill_no)

    def get_bill_info(self, bill_no: str) -> dict:
        """
        Retrieves detailed bill information from the National Assembly API.

        Parameters:
            bill_no (str): The BILL_NO of the bill to fetch information for.

        Returns:
            dict: A dictionary containing bill details such as BILL_NO, BILL_NM, and LINK_URL.
        """
        api_url = f"https://open.assembly.go.kr/portal/openapi/ALLBILL?KEY={self.na_api_key}&BILL_NO={bill_no}"
        response = requests.get(api_url)

        if response.status_code != 200:
            logger.error(
                f"Error: Failed to fetch data, status code {response.status_code}"
            )
            return None
        try:
            root = ET.fromstring(response.content)
            result_code = root.find(".//CODE").text
            if result_code != "INFO-000":

                logger.error(f"Error: {root.find('.//MESSAGE').text}")
                return None

            bill_info = {
                "BILL_NO": root.find(".//BILL_NO").text,
                "BILL_ID": root.find(".//BILL_ID").text,
                "BILL_NM": root.find(".//BILL_NM").text,
                "PPSL_DT": root.find(".//PPSL_DT").text,
                "RGS_CONF_RSLT": root.find(".//RGS_CONF_RSLT").text,
                "LINK_URL": root.find(".//LINK_URL").text,
            }

            self.bill_info = bill_info
            return bill_info

        except ET.ParseError as e:

            logger.error(f"Error: Failed to parse XML - {str(e)}")
            logger.error(f"Error: Response content - {response.text}")
            return None

    def get_bill_id(self):
        return self.bill_info["BILL_ID"]

    def get_soup(self, bill_link: str) -> BeautifulSoup:
        """
        Retrieves and parses the HTML content of the bill webpage.

        Parameters:
            bill_link (str): The URL of the bill webpage.

        Returns:
            BeautifulSoup: Parsed HTML content of the bill's webpage.
        """
        response = requests.get(bill_link)

        if response.status_code != 200:
            return None
        return BeautifulSoup(response.content, "html.parser")

    def get_bill_summary(self) -> str:
        """
        Extracts the bill summary from the bill's webpage.

        Returns:
            str: The summary of the bill.
        """
        try:
            return self.bill_soup.find("div", {"id": "summaryContentDiv"}).text.strip()
        except Exception as e:
            logger.error(f"Error: summaryContentDiv not found - {str(e)}")
            return ""

    def get_bill_no_pdf_url(self) -> tuple:
        """
        Extracts the BILL_NO and PDF URL from the bill's webpage.

        Returns:
            tuple: A tuple containing the BILL_NO and the PDF URL of the bill.
        """
        # Find the div element with the class "tableCol01" that contains the table

        try:
            table_div = self.bill_soup.find("div", class_="tableCol01")
        except Exception as e:
            logger.error(f"Error: Div with class 'tableCol01' not found. - {str(e)}")
            return ""

        table = table_div.find(
            "table",
            summary="의안접수정보의 의안번호, 제안일자, 제안자, 문서, 제안회기 정보",
        )
        if not table:
            return "Table not found.", None

        tbody = table.find("tbody")
        if not tbody:
            return "Table body not found.", None

        rows = tbody.find_all("tr")
        if not rows:
            return "No rows found in the table.", None

        # Extract bill_no from the first <td> in the first row
        bill_no_td = rows[0].find_all("td")[0]
        bill_no = bill_no_td.text.strip()  # Remove extra spaces or newlines

        # Find the 4th <td> element in the first row that contains the PDF link
        target_td = rows[0].find_all("td")[3]
        links = target_td.find_all("a")
        if len(links) < 2:
            return bill_no, "PDF URL not found."

        # Handle JavaScript link that contains the PDF file information
        javascript_link = links[1].get("href")
        # Use regex to extract the file ID from the JavaScript function call
        match = re.search(
            r"openBillFile\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)",
            javascript_link,
        )
        if not match:
            logger.error(
                f"error: PDF URL extraction failed. Regex did not match. {str(table)}"
            )
            return bill_no, "PDF URL extraction failed. Regex did not match."

        file_id = match.group(2)
        self.bill_no = bill_no
        self.pdf_url = f"https://likms.assembly.go.kr/filegate/sender24?dummy=dummy&bookId={file_id}&type=1"
        # Return both the bill number and the PDF URL
        return bill_no, self.pdf_url

    def save_bill(self, host, user, password):
        """
        Save to Database.

        Parameters:
            host (str): Database host ip ex) localhost.
            user (str): User name in database ex) root.
            password (str): Password for user.
        """

        params = (
            self.bill_info["BILL_ID"],
            self.bill_info["LINK_URL"],
            self.bill_info["BILL_NO"],
            self.bill_info["BILL_NM"],
            self.bill_summary,
            self.pdf_url,
            self.bill_info["PPSL_DT"],
            self.bill_info["BILL_NO"][:2],
        )
        db_manager.save_bill(params=params)


class All_BillIdsExtractor:
    def __init__(self, host, user, password):
        self.results = db_manager.read_all_value_table("bill_summary", "bill_id")
        print(db_manager.read_all_value_table("bill_summary", "bill_id"))
        logger.debug("All_BillIdsExtractor get:" + str(len(self.results)))


class All_KeywordExtractor:
    def __init__(self, host, user, password):
        self.results = []
        keylist = ["keyword1", "keyword2", "keyword3"]
        for column in keylist:
            table = "bill"
            results = db_manager.read_all_value_table(table, column)
            if not results is None:
                self.results += [reulst[0] for reulst in results]
        self.results = list(set(self.results))


class KeywordExtractor:
    def __init__(self, bill_id):

        self.bill_id = bill_id

        table = "bill_summary"
        result = db_manager.read_value_table(table, "bill_id", bill_id)
        self.headline = result[1]
        self.sumary = result[2]

    def get_keyword(self):
        text = self.sumary
        if self.sumary == "":
            logger.info("Info: Try get_beywords but empty summary")
            return
        system_instructions = """주어진 문단을 분류하기 위해 사용하기 적절한 단어 3가지를 골라서 아래 예시와 같이 출력해줘
        예시 : 장애인, 복지, 교통"""
        model = "gemini-1.5-flash"
        temperature = 0
        stop_sequence = "종료!"

        self.ggl_api_key = api_keyManager.get_ggl_api_key()
        genai.configure(api_key=self.ggl_api_key)

        model = genai.GenerativeModel(model, system_instruction=system_instructions)
        config = genai.GenerationConfig(
            temperature=temperature, stop_sequences=[stop_sequence]
        )
        response = model.generate_content(contents=[text], generation_config=config)
        sentence = response.text
        extracted = [part.strip() for part in sentence.split(",")]
        self.get_keywords = extracted
        return extracted

    def save_keyword(self):
        table = "bill"
        column = "bill_id"
        set_columns = [
            "keyword1",
            "keyword2",
            "keyword3",
        ]
        for index, set_column in enumerate(set_columns):
            db_manager.update_value(
                table, column, self.bill_id, set_column, self.get_keywords[index]
            )


class AllScheduleExtractor:
    def __init__(self):
        """
        Initializes the AllScheduleExtractor class.

        - Instantiates an APIKeyManager to handle API keys.
        - Retrieves the National Assembly API key.
        - Initializes an empty list to store the full schedule.
        - Calls the function to get all schedule data and sets up the latest schedule.
        """
        self.na_api_key = api_keyManager.get_na_api_key()
        self.all_schedule = []
        self.get_all_schedule()
        self.all_latest_schedule = self.get_latest_schedule()

    def get_all_schedule(self):
        """
        Retrieves and stores all available schedule information from the National Assembly API.

        This function sends a GET request to the API, retrieves schedule data, parses it,
        and appends relevant information to the `self.all_schedule` list.

        Returns:
        - list: A list of dictionaries, each containing schedule information.
        """
        # Base URL for the API
        base_url = "https://open.assembly.go.kr/portal/openapi/ALLSCHEDULE"

        # Define the parameters to send to the API
        params_dict = {
            "KEY": self.na_api_key,
            "Type": "json",  # Response type as JSON
            "pSize": 1000,  # Adjust this parameter for desired no of schedules
        }

        # Send the GET request
        response = requests.get(base_url, params=params_dict)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            schedule_data = response.json()

            # Iterate through each row in the schedule and extract relevant information
            for sch in schedule_data["ALLSCHEDULE"][1]["row"]:
                schedule_info = {
                    "SCH_KIND": sch.get("SCH_KIND", ""),
                    "SCH_CN": sch.get("SCH_CN", ""),
                    "SCH_DT": sch.get("SCH_DT", ""),
                    "SCH_TM": sch.get("SCH_TM", ""),
                    "CONF_DIV": sch.get("CONF_DIV", ""),
                    "CMIT_NM": sch.get("CMIT_NM", ""),
                    "CONF_SESS": sch.get("CONF_SESS", ""),
                    "CONF_DGR": sch.get("CONF_DGR", ""),
                    "EV_INST_NM": sch.get("EV_INST_NM", ""),
                    "EV_PLC": sch.get("EV_PLC", ""),
                }
                # Append the schedule information to the list
                self.all_schedule.append(schedule_info)

            return self.all_schedule

        else:
            # Handle the error if the request was not successful
            logger.error(
                f"error: GET request failed with status code {response.status_code}"
            )

    def get_future_schedule(self):
        """
        Filters and returns schedules that are set for future dates.

        Uses the 'SCH_DT' field from the schedule and compares it with the current date.

        Returns:
        - list: A list of dictionaries with schedules in the future.
        """
        future_schedule_list = list(
            filter(
                lambda sch: datetime.strptime(sch["SCH_DT"], "%Y.%m.%d")
                > datetime.now(),
                self.all_schedule,
            )
        )

        return future_schedule_list

    def get_past_schedule(self):
        """
        Filters and returns schedules that are in the past.

        Uses the 'SCH_DT' field from the schedule and compares it with the current date.

        Returns:
        - list: A list of dictionaries with schedules that are in the past.
        """
        past_schedule_list = list(
            filter(
                lambda sch: datetime.strptime(sch["SCH_DT"], "%Y.%m.%d")
                < datetime.now(),
                self.all_schedule,
            )
        )

        return past_schedule_list

    def get_latest_schedule(self):
        """
        Retrieves and returns the latest past schedule.

        Filters the schedule list for past schedules and returns the most recent one.

        Returns:
        - dict: A dictionary containing the most recent past schedule.
        """
        past_schedule_list = list(
            filter(
                lambda sch: datetime.strptime(sch["SCH_DT"], "%Y.%m.%d")
                < datetime.now(),
                self.all_schedule,
            )
        )

        return past_schedule_list[0]  # Returns the most recent past schedule


class ConfScheduleExtractor:
    def __init__(self, unit_cd):
        """
        Initializes the ConfScheduleExtractor class.

        - Instantiates an APIKeyManager to handle API keys.
        - Retrieves the National Assembly API key.
        - Initializes an empty list to store conference-specific schedules.
        - Calls the function to get schedules based on unit code and sets up the latest schedule.

        Parameters:
        - unit_cd (str): The unit code for the desired conference.
        """
        self.na_api_key = api_keyManager.get_na_api_key()
        self.conf_schedule = []
        self.get_conf_schedule(unit_cd)
        self.conf_latest_schedule = self.get_latest_schedule()

    def get_conf_schedule(self, unit_cd):
        """
        Retrieves and stores schedule information for a specific conference using its unit code.

        Sends a GET request to the API with the provided unit code, retrieves data, and appends
        relevant information to the `self.conf_schedule` list.

        Parameters:
        - unit_cd (str): The unit code of the conference for which the schedule is being requested.

        Returns:
        - list: A list of dictionaries, each containing conference schedule information.
        """
        # Base URL for the API
        base_url = "https://open.assembly.go.kr/portal/openapi/nekcaiymatialqlxr"

        # Define the parameters to send to the API
        params_dict = {
            "KEY": self.na_api_key,
            "Type": "json",  # Response type as JSON
            "pSize": 100,  # Adjust this parameter for desired no of schedules
            "UNIT_CD": unit_cd,
        }

        # Send the GET request
        response = requests.get(base_url, params=params_dict)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            schedule_data = response.json()
            # Iterate through each row in the schedule and extract relevant information
            for sch in schedule_data["nekcaiymatialqlxr"][1]["row"]:
                schedule_info = {
                    "MEETINGSESSION": sch.get("MEETINGSESSION", ""),
                    "CHA": sch.get("CHA", ""),
                    "TITLE": sch.get("TITLE", ""),
                    "MEETTING_DATE": sch.get("MEETTING_DATE", ""),
                    "MEETTING_TIME": sch.get("MEETTING_TIME", ""),
                    "LINK_URL": sch.get("LINK_URL", ""),
                    "UNIT_CD": sch.get("UNIT_CD", ""),
                    "UNIT_NM": sch.get("UNIT_NM", ""),
                }
                # Append the schedule information to the list
                self.conf_schedule.append(schedule_info)

            return self.conf_schedule

        else:
            # Handle the error if the request was not successful
            logger.error(
                f"error: GET request failed with status code {response.status_code}"
            )

    def get_latest_schedule(self):
        """
        Retrieves and returns the most recent conference schedule from the list.

        Returns:
        - dict: A dictionary containing the most recent conference schedule.
        """
        return self.conf_schedule[0]  # Returns the most recent schedule


if __name__ == "__main__":
    # Example of using the AllScheduleExtractor class
    ase = AllScheduleExtractor()
    print(ase.all_schedule[0])  # Print the first schedule
    print(ase.all_latest_schedule)  # Print the latest past schedule

    # Example of using the ConfScheduleExtractor class with a specific DAE unit code
    cse = ConfScheduleExtractor("100022")
    print(cse.conf_schedule[0])  # Print the first conference schedule
    print(cse.conf_latest_schedule)  # Print the latest conference schedule
