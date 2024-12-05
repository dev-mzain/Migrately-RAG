import io
import textwrap

import requests
from fpdf import FPDF


def upload_to_fileio(file_content):
    # Read the file content into memory using io.BytesIO

    # Send a POST request to the File.io API with the file content
    response = requests.post('https://file.io', files={'file': file_content})

    # Check if the response is successful
    if response.status_code == 200:
        # Return the download link from the response
        print(response.json()['link'])
        return response.json()['link']
    else:
        # Handle errors
        return f"Error uploading file: {response.status_code}, {response.text}"


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

