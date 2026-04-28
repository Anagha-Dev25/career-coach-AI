import os
from dotenv import load_dotenv

load_dotenv()  # This looks for the .env file

API_KEY = os.getenv("OPENAI_API_KEY")