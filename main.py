from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from services.openai import summarize_and_categorize_document, prepare_case
from services.storage import upload_to_fileio
from utils.database import store_metadata, get_all_summaries
from utils.vector_db import summarize_document

app = FastAPI()

@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    descriptions: List[str] = []
):
    # Ensure the number of files matches the number of descriptions
    if len(files) != len(descriptions):
        raise HTTPException(
            status_code=400,
            detail="The number of files and descriptions must match."
        )

    results = []

    for file, description in zip(files, descriptions):
        # Read file content
        content = await file.read()  # Read the file content as bytes
        document_text = content.decode('utf-8')  # Decode bytes to string

        metadata = {
            "description": description,
            "file_name": file.filename,
        }

        context = summarize_document(document_text, metadata)
        summary, document_category = await summarize_and_categorize_document(context)
        file_location = upload_to_fileio(document_text)
        print(summary)
        print(document_category)
        # Prepare metadata for this document
        metadata["category"] = document_category
        metadata["file_location"] = file_location
        metadata["summary"] = summary

        # Store metadata in database
        store_metadata(metadata)

        # Append result for this file
        results.append({
            "file_name": file.filename,
            "category": document_category,
            "summary": summary,
            "description": description,
        })

    return {
        "message": f"{len(files)} document(s) uploaded and processed successfully.",
        "results": results
    }


@app.get("/summaries")
async def get_summaries():
    # Get summaries for all categories
    summaries = get_all_summaries()
    return {"summaries": summaries}



@app.get("/case")
async def generate_case():
    # Generate case statement
    case = await prepare_case()
    return {"case": case}
