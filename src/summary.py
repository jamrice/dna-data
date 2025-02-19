import google.generativeai as genai
from src.load import api_keyManager
from src.extractors import BillExtractor
from src.dna_logger import logger
from src.db_handler import db_manager


class Summarizer:

    def __init__(self, bill_summary: str):
        """
        Initializes the Summarizer class by configuring the Google Generative AI API with
        the Google API key and setting up the BillExtractor to fetch bill summaries.
        """
        self.bill_summary = bill_summary
        self.ggl_api_key = api_keyManager.get_ggl_api_key()
        genai.configure(api_key=self.ggl_api_key)
        try:
            self.headline = ""
            self.summarize_headline()
            self.paragraph = ""
            self.summarize_paragraph()
        except Exception as e:
            logger.error(f"Error: summarize error occurred {str(e)}")
        self.bill_id = None
        self.conf_id = None

    def summarize_headline(self):
        """
        Summarizes the bill's content into a single headline using generative AI.

        This method calls the BillExtractor to retrieve the bill summary, and uses
        the generative AI model 'gemini-1.5-flash' to summarize it into a headline
        in a friendly and polite tone with simpler language.

        Returns:
        str: The generated headline.
        """
        text = self.bill_summary
        if self.bill_summary == "":
            logger.info("Info: empty summary")
            return
        system_instructions = "주어진 문단을 한 문장으로 요약하는데, 어려운 말을 쉬운 말로 풀어서 설명하되 존댓말로 말하는 친절한 말투로 해줘"
        model = "gemini-1.5-flash"
        temperature = 0
        stop_sequence = "종료!"
        model = genai.GenerativeModel(model, system_instruction=system_instructions)
        config = genai.GenerationConfig(
            temperature=temperature, stop_sequences=[stop_sequence]
        )
        response = model.generate_content(contents=[text], generation_config=config)
        self.headline = response.text
        return response.text

    def summarize_paragraph(self):
        """
        Summarizes the bill's content into a paragraph using generative AI.

        This method calls the BillExtractor to retrieve the bill summary, and uses
        the generative AI model 'gemini-1.5-flash' to simplify the language in the
        summary while maintaining a polite tone in a longer form.

        Returns:
        str: The generated paragraph.
        """
        text = self.bill_summary
        system_instructions = "주어진 문단을 어려운 말을 쉬운 말로 풀어서 설명하되 존댓말로 말하는 친절한 말투로 해줘"
        model = "gemini-1.5-flash"
        temperature = 0
        stop_sequence = "종료!"
        model = genai.GenerativeModel(model, system_instruction=system_instructions)
        config = genai.GenerationConfig(
            temperature=temperature, stop_sequences=[stop_sequence]
        )
        response = model.generate_content(contents=[text], generation_config=config)
        self.paragraph = response.text
        return response.text

    def translate_to_english(self):
        """
        Translates the bill's summary into English using generative AI.

        This method uses the generative AI model 'gemini-1.5-flash' to translate
        the summary into English.

        Returns:
        str: The translated summary in English.
        """
        text = self.bill_summary
        if self.bill_summary == "":
            logger.info("Info: empty summary")
            return

        system_instructions = "주어진 문단을 영어로 번역해줘"
        model = "gemini-1.5-flash"
        temperature = 0
        stop_sequence = "종료!"
        model = genai.GenerativeModel(model, system_instruction=system_instructions)
        config = genai.GenerationConfig(
            temperature=temperature, stop_sequences=[stop_sequence]
        )
        response = model.generate_content(contents=[text], generation_config=config)
        return response.text

    def get_headline(self):
        """
        Returns the generated headline.

        Returns:
        str: The headline generated by the summarize_headline method.
        """
        return self.headline

    def get_paragraph(self):
        """
        Returns the generated paragraph.

        Returns:
        str: The paragraph generated by the summarize_paragraph method.
        """
        return self.paragraph

    def save_summary(self, host, user, password):
        """
        Save to Database.

        Parameters:
            host (str): Database host ip ex) localhost.
            user (str): User name in database ex) root.
            password (str): Password for user.
        """
        columns = ("headline", "body", "bill_id", "conf_id")
        params = (
            self.get_headline(),
            self.get_paragraph(),
            self.bill_id,
            self.conf_id,
        )
        table = "bill_summary"
        db_manager.save_table(table, columns, params)


if __name__ == "__main__":
    be = BillExtractor(
        "https://likms.assembly.go.kr/bill/billDetail.do?billId=PRC_U2Y3E0F8G0A9G1U0G0N9R0R0M1F0U0"
    )
    summarizer = Summarizer(be.bill_summary)
    print("Headline : ", summarizer.get_headline())
    print("Paragraph : ", summarizer.get_paragraph())
