import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from fastapi.responses import FileResponse
from services.openai import summarize_and_categorize_document, prepare_case
from services.storage import upload_to_fileio, text_to_pdf
from utils.database import store_metadata, get_all_summaries, get_latest_case_statement
from utils.vector_db import summarize_document
import logging
import fitz

# Initialize FastAPI app
app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...), descriptions: List[str] = []):
    if len(files) != len(descriptions):
        raise HTTPException(
            status_code=400,
            detail="The number of files and descriptions must match."
        )

    results = []
    for file, description in zip(files, descriptions):
        try:
            result = await process_document(file, description)
            results.append(result)
        except HTTPException as e:
            # Continue processing other documents even if one fails
            logger.error(f"Skipping {file.filename} due to error: {e.detail}")
            continue

    return {
        "message": f"{len(files)} document(s) uploaded and processed successfully.",
        "results": results
    }


@app.get("/summaries")
async def get_summaries():
    try:
        summaries = get_all_summaries()
        return {"summaries": summaries}
    except Exception as e:
        logger.error(f"Error retrieving summaries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve summaries.")


@app.get("/case")
async def generate_case():
    try:
        case = await prepare_case()
        return {"case": case}
    except Exception as e:
        logger.error(f"Error generating case: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate case statement.")


@app.get("/case/latest")
async def get_latest_case():
    latest_case = get_latest_case_statement()
    if not latest_case:
        raise HTTPException(status_code=404, detail="No case statements found.")
    return {"latest_case": latest_case}


@app.get("/case/latest/download")
async def download_latest_case():
    latest_case = get_latest_case_statement()
    if not latest_case:
        raise HTTPException(status_code=404, detail="No case statements found.")

    pdf_file_path = "latest_case_statement.pdf"

    try:
        # Generate the PDF
        text_to_pdf(latest_case, pdf_file_path)

        if os.path.exists(pdf_file_path):
            return FileResponse(
                pdf_file_path,
                media_type="application/pdf",
                filename="case_statement.pdf"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate the PDF.")

    except Exception as e:
        logger.error(f"Error generating or sending the PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate or download the case PDF.")


# Helper function to handle document processing
async def process_document(file: UploadFile, description: str) -> dict:
    try:
        # Read file content
        content = await file.read()

        # Check if file is a PDF
        if file.content_type == 'application/pdf':
            # Extract text from PDF using PyMuPDF (fitz)
            document_text = extract_text_from_pdf(content)
        else:
            # If it's not a PDF, assume it's a text file and decode
            document_text = content.decode('utf-8')

        metadata = {
            "description": description,
            "file_name": file.filename,
        }

        context = summarize_document(document_text, metadata)
        summary, document_category = await summarize_and_categorize_document(context)
        file_location = upload_to_fileio(document_text)

        # Log document processing details
        logger.info(f"Processed document: {file.filename}, Category: {document_category}")

        # Prepare metadata
        metadata["category"] = document_category
        metadata["file_location"] = file_location
        metadata["summary"] = summary

        # Store metadata in database
        store_metadata(metadata)

        return {
            "file_name": file.filename,
            "category": document_category,
            "summary": summary,
            "description": description,
        }

    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document {file.filename}.")

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_content: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        document_text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            document_text += page.get_text()
        return document_text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")
