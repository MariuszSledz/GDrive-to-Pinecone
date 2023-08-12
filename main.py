import os
import pinecone
import json
from langchain.document_loaders import PyPDFLoader
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

def authenticate_google_drive():
    # Load the credentials from the file and authenticate
    creds_dict = json.loads(os.environ.get('GDRIVE_CREDENTIALS'))
    creds = service_account.Credentials.from_service_account_info(creds_dict)
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

def get_new_files(drive_service):
    # Query the Google Drive folder for new files
    folder_id = os.environ['FOLDER_ID']
    query = f"'{folder_id}' in parents and mimeType='application/pdf'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files

def download_file(drive_service, file_id, file_name):
    # Get the file's metadata to access the webViewLink
    file_metadata = drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
    web_view_link = file_metadata['webViewLink']

    # Download the file
    request = drive_service.files().get_media(fileId=file_id)
    response = request.execute()
    with open(file_name, 'wb') as file:
        file.write(response)

    return file_name, web_view_link

def process_and_upload(file_path, filename, web_view_link):
    # Process the document and upload to Pinecone
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    print(f"Uploading {filename} to Pinecone database")
    
    # Include the Google Drive link in the metadata for each page
    metadatas = [{"web_view_link": web_view_link, **t.metadata} for t in pages]
    embeddings = OpenAIEmbeddings()
    index_name = os.environ.get('INDEX_NAME', None)
    Pinecone.from_texts([t.page_content for t in pages], metadatas=metadatas, embedding=embeddings, index_name=index_name)
    
    # Delete the local file after processing
    try:
        os.remove(file_path)
        print(f"Successfully deleted local file {file_path}")
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")

# Function to load processed files
def load_processed_files():
    try:
        with open('processed_files.txt', 'r') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to save processed file ID
def save_processed_file(file_id):
    with open('processed_files.txt', 'a') as file:
        file.write(f"{file_id}\n")

def main():
    # Authenticate GDrive
    drive_service = authenticate_google_drive()

    #initialise pinecone
    pinecone.init(
        api_key = os.environ.get("PINECONE_API_KEY", None),
        environment = os.environ.get("ENIVROMENT_NAME", None),
    )
    # Load processed files
    processed_files = load_processed_files()
    new_files = get_new_files(drive_service)

    # Process new files
    for file in new_files:
        file_id = file['id']
        file_name = file['name']

        # Skip if file has already been processed
        if file_id in processed_files:
            print(f"Skipping already processed file: {file_name}")
            continue

        file_path, web_view_link = download_file(drive_service, file_id, file_name)
        process_and_upload(file_path, file_name, web_view_link)

        # Save processed file ID
        save_processed_file(file_id)

if __name__ == '__main__':
    main()