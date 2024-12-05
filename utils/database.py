import logging
from pymongo import MongoClient
from datetime import datetime
from config import variables

# Set up logging for better monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection setup
client = MongoClient(variables.DATABASE_URL)
db = client.o1_visa_db
metadata_collection = db.metadata
cases_collection = db.cases

def store_metadata(metadata: dict):
    """
    Store metadata in the database.
    """
    try:
        metadata_collection.insert_one(metadata)
        logger.info(f"Metadata for {metadata.get('file_name', 'unknown')} stored successfully.")
    except Exception as e:
        logger.error(f"Error storing metadata: {e}")
        raise Exception(f"Failed to store metadata: {e}")


def get_all_summaries():
    """
    Retrieve all summaries from the database, group them by their distinct categories,
    and return the result as a dictionary.
    """
    try:
        # Fetch all metadata documents and group by category
        documents = metadata_collection.find({}, {"category": 1, "summary": 1})

        # Initialize a dictionary to group summaries by categories
        categorized_summaries = {
            "Published Material": [],
            "Awards and Recognitions": [],
            "High Remuneration Evidence": [],
            "Uncategorized": []
        }

        # Iterate through each document and categorize the summaries
        for doc in documents:
            category = doc.get("category", "Uncategorized")
            summary = doc.get("summary")

            if summary:
                categorized_summaries.setdefault(category, []).append(summary)

        return categorized_summaries

    except Exception as e:
        logger.error(f"Error retrieving summaries: {e}")
        raise Exception("Failed to retrieve summaries.")


def store_case_statement(case_statement: str):
    """
    Store the case statement with a timestamp in the database.
    """
    try:
        case_document = {
            "case_statement": case_statement,
            "created_at": datetime.utcnow()
        }
        cases_collection.insert_one(case_document)
        logger.info("Case statement stored successfully.")
    except Exception as e:
        logger.error(f"Error storing case statement: {e}")
        raise Exception("Failed to store case statement.")


def get_latest_case_statement():
    """
    Retrieve the latest case statement based on the timestamp.
    """
    try:
        latest_case = cases_collection.find_one(sort=[("created_at", -1)])

        if latest_case:
            return latest_case.get("case_statement")
        else:
            logger.info("No case statements found.")
            return None

    except Exception as e:
        logger.error(f"Error retrieving latest case statement: {e}")
        raise Exception("Failed to retrieve the latest case statement.")
