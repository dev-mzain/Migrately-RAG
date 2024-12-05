
from dotenv import load_dotenv
import os


load_dotenv()

class Variables:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    PINECONE_KEY: str = os.getenv("PINECONE_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")


variables = Variables()
