# GDrive to Pinecone Document Uploader

This project automatically fetches PDF documents from a specified Google Drive folder and uploads them to Pinecone, page by page. It uses Google Drive API for accessing the files, PyPDFLoader for reading the PDFs, and Pinecone for vector storage. The application is designed to be deployed on Heroku and uses a scheduler to check for new files constantly.

## Prerequisites

- Google Drive API credentials (service account)
- Pinecone API key
- Heroku account (for deployment)

## Environment Variables

Create a `.env` file in your project directory and define the following environment variables:

- `GDRIVE_CREDENTIALS`: JSON string containing the Google Drive API credentials.
- `FOLDER_ID`: The ID of the Google Drive folder containing the PDF documents.
- `PINECONE_API_KEY`: Your Pinecone API key.
- `INDEX_NAME`: The name of the Pinecone index where the documents will be stored.
- `ENVIRONMENT_NAME`: (Optional) Pinecone environment name, if any.

## Local Setup

1. Clone the repository.
2. Install the required dependencies.
3. Run `python main.py` to start the application.

## Deployment to Heroku

1. Create a new Heroku app.
2. Add the Heroku Scheduler add-on.
3. Configure the environment variables in the Heroku dashboard.
4. Deploy the code to Heroku.
5. Configure the scheduler to run the script at your desired interval.

## Google Drive Folder Access

The folder on Google Drive containing the documents must have general access for "Anyone with the link." You can configure this setting in the sharing options for the folder in Google Drive.

## Note on Processing

The script includes logic to avoid processing the same files multiple times. Processed file IDs are saved in a file named `processed_files.txt`. If you need to reprocess files, you can modify or delete this file.

## Contributing

If you have any suggestions, bug reports, or contributions, please open an issue or pull request.

## License

This project is licensed under the MIT License.
