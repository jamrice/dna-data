import os
from dotenv import load_dotenv


class APIKeyManager:
    """
    Manages API keys for accessing services such as the National Assembly API and Google API.
    """

    def __init__(self):
        """
        Initializes the APIKeyManager class by loading API keys from environment variables.
        """
        load_dotenv()
        self.na_api_key = os.getenv("NationalAssemblyAPI")
        self.ggl_api_key = os.getenv("GOOGLE_API_KEY")
        self.db_password = os.getenv("DATABASE_PASSWORD")

    def get_na_api_key(self) -> str:
        """
        Retrieves the National Assembly API key.

        Returns:
            str: The National Assembly API key.
        """
        return self.na_api_key

    def get_ggl_api_key(self) -> str:
        """
        Retrieves the Google API key.

        Returns:
            str: The Google API key.
        """
        return self.ggl_api_key

    def get_db_password(self) -> str:
        """
        Retrieves the database password.

        Returns:
            str: The database password.
        """
        return self.db_password

    def print_key(self):
        """
        Prints the API keys for debugging or verification purposes.
        """
        print("na_api_key : ", self.na_api_key)
        print("ggl_api_key : ", self.ggl_api_key)


api_keyManager = APIKeyManager()
api_keyManager.print_key()
