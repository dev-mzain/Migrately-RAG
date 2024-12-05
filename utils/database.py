from pymongo import MongoClient
from config import variables

client = MongoClient(variables.DATABASE_URL)

db = client.o1_visa_db
metadata_collection = db.metadata
summaries_collection = db.summaries

def store_metadata(metadata: dict):
    metadata_collection.insert_one(metadata)

def store_summary(document_id: str, summary: str):
    summaries_collection.insert_one({"_id": document_id}, {"$set": {"summary": summary}}, upsert=True)


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

