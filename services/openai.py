import openai
from utils.database import  get_all_summaries
from config import variables


openai.api_key = variables.OPENAI_API_KEY
async def summarize_and_categorize_document(document_text: str):
    """
    Summarize and categorize the document into one of the predefined categories:
    Published Material, Awards and Recognitions, High Remuneration Evidence.
    """

    # Create the prompt to both summarize and categorize the document
    prompt = f"""
    Please perform the following tasks for the document below:
    1. Summarize the content efficiently.
    2. Categorize the document into one of the following categories: 
       Published Material, Awards and Recognitions, High Remuneration Evidence.

    Please return the results in the following format:
    - Summary: <summary of the document>
    - Category: <chosen category>

    Document: {document_text}
    """

    # Make a request to OpenAI to both summarize and categorize the document using chat-based API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        result = response.choices[0].message['content'].strip()
        print(result)
        # Parse the result into summary and category
        # Assuming result is returned in the format of "Summary: <summary> Category: <category>"
        summary, category = None, None
        try:
            summary_start = result.index("Summary:") + len("Summary:")
            category_start = result.index("Category:") + len("Category:")

            summary = result[summary_start:category_start].strip()
            category = result[category_start:].strip()

        except ValueError:
            # Return default error values if parsing fails
            summary = "Error: Unable to parse summary."
            category = "Error: Unable to categorize."

        # Always return a tuple (summary, category)
        return summary, category

    except Exception as e:
        # Handle any other exceptions and ensure two values are returned
        return "Error: Failed to generate summary.", "Error: Failed to categorize."



async def prepare_case():
    """
    Prepare a case statement for O-1 visa qualification based on all document summaries.
    """
    summaries = get_all_summaries()

    # Prompt GPT to analyze all summaries and prepare a case statement
    prompt = f"Based on the following document summaries, prepare a case statement on how well the client qualifies for an O-1 visa:\n\n{summaries}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    case_statement = response.choices[0].message['content'].strip()

    return case_statement
