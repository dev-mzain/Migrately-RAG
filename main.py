from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
from fastapi.responses import FileResponse

from services.openai import summarize_and_categorize_document, prepare_case
from services.storage import upload_to_fileio
from utils.database import store_metadata, get_all_summaries, get_latest_case_statement
from utils.vector_db import summarize_document
from fpdf import FPDF
import textwrap
import os
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


@app.get("/case/latest")
async def get_latest_case():
    """
    Retrieve the latest case statement from the database.
    """
    latest_case = get_latest_case_statement()
    if not latest_case:
        raise HTTPException(
            status_code=404, detail="No case statements found."
        )
    return {"latest_case": latest_case}


def text_to_pdf(text, filename):
    """
    Convert text to a PDF file.
    """
    a4_width_mm = 210  # Width of A4 paper in mm
    pt_to_mm = 0.35  # Conversion factor from points to mm
    fontsize_pt = 10  # Font size in points
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10  # Bottom margin in mm
    character_width_mm = 7 * pt_to_mm  # Approximate character width in mm
    width_text = a4_width_mm / character_width_mm  # Number of characters per line

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, int(width_text))

        if len(lines) == 0:
            pdf.ln()  # Add a blank line if there's an empty line

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename)

@app.get("/case/latest/download")
async def download_latest_case():
    """
    Generate and download the latest case statement as a PDF.
    """
    latest_case = get_latest_case_statement()
    if not latest_case:
        raise HTTPException(
            status_code=404, detail="No case statements found."
        )

    # File name for the PDF
    pdf_file_path = "latest_case_statement.pdf"

    # Generate the PDF
    text_to_pdf(latest_case, pdf_file_path)

    # Return the PDF file as a response
    if os.path.exists(pdf_file_path):
        return FileResponse(
            pdf_file_path,
            media_type="application/pdf",
            filename="case_statement.pdf"
        )
    else:
        raise HTTPException(
            status_code=500, detail="Failed to generate the PDF."
        )
