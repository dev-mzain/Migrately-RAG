from pymongo import MongoClient
from datetime import datetime
from config import variables

# MongoDB connection
client = MongoClient(variables.DATABASE_URL)
db = client.o1_visa_db
metadata_collection = db.metadata
cases_collection = db.cases

def store_metadata(metadata: dict):
    metadata_collection.insert_one(metadata)


def get_all_summaries():
    """
    Retrieve all summaries from the database, group them by their distinct categories,
    and return the result as a dictionary.
    """
    # Fetch all metadata documents
    documents = metadata_collection.find()

    # Initialize a dictionary to group summaries by categories
    categorized_summaries = {
        "Published Material": [],
        "Awards and Recognitions": [],
        "High Remuneration Evidence": [],
        "Uncategorized": []
    }

    # Iterate through each document
    for doc in documents:
        category = doc.get("category", "Uncategorized")
        summary_doc = metadata_collection.find_one({"_id": doc["_id"]})

        if summary_doc and "summary" in summary_doc:
            summary = summary_doc["summary"]
            # Append the summary to the respective category
            if category in categorized_summaries:
                categorized_summaries[category].append(summary)
            else:
                categorized_summaries["Uncategorized"].append(summary)

    return categorized_summaries


def store_case_statement(case_statement: str):
    """
    Store the case statement with a timestamp in the database.
    """
    case_document = {
        "case_statement": case_statement,
        "created_at": datetime.utcnow()
    }
    cases_collection.insert_one(case_document)


def get_latest_case_statement():
    """
    Retrieve the latest case statement based on the timestamp.
    """
    latest_case = cases_collection.find_one(sort=[("created_at", -1)])
    if latest_case:
        return latest_case["case_statement"]
    return None
