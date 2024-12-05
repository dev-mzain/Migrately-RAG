import io
import requests

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

