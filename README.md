
# Migrately-RAG: Document Categorization, Summarization, and Case Preparation for O-1 Visa Applications


Migrately-RAG is a FastAPI-based application designed to automate document processing for tasks such as categorization, summarization, and case preparation. Built for use cases like O-1 visa applications, it leverages advanced AI technologies for text processing, vector embedding, and data storage.

---
## **Acceptance Criteria**

All acceptance creiteria are fullfilled:

1. Accurate categorization of documents into predefined folders.
2. AI-generated summaries for each category are relevant and concise.
3. The case preparation highlights the user’s qualifications effectively.
4. All functionality is accessible via API endpoints.

---

## **Features**
- **Document Upload and Processing**: Upload multiple documents, automatically summarize and categorize them, and securely store metadata.
- **Summary Retrieval**: Fetch summaries grouped by category for easy access and analysis.
- **Case Preparation**: Generate comprehensive case statements tailored to O-1 visa applications.
- **Cloud-Based Storage**: Securely store uploaded documents in the cloud and access them via download links.

---

## **Tech Stack**
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [MongoDB](https://www.mongodb.com/) for metadata storage
- **AI Integration**: [OpenAI GPT](https://openai.com/) for summarization and case preparation
- **Embedding and Querying**: [Pinecone](https://www.pinecone.io/) Vector Database for embedding storage and document context retrieval
- **Cloud Storage**: [file.io](https://www.file.io/) for document storage
- **PDF Generation**: [FPDF](http://www.fpdf.org/) for creating downloadable case statements
- **Deployment**: Hosted on [Koyeb](https://www.koyeb.com/)

---

## **API Documentation**
- **API Documentation:** https://concerned-carine-algorythm-27f8c324.koyeb.app/docs 

---

## **Endpoints**

### 1. **POST** `/upload`
- **Description**: Handles multiple document uploads and processes them.
- **Flow**:
  1. Uploads documents to cloud storage and retrieves download links.
  2. Generates embedding vectors for the documents and descriptions.
  3. Queries the vector database to summarize document context.
  4. Passes the context to OpenAI GPT to generate:
     - A readable summary.
     - A category for the document.
  5. Stores metadata in MongoDB:
     - Document cloud link
     - Generated summary
     - Document category
     - Additional metadata

---

### 2. **GET** `/summaries`
- **Description**: Retrieves summaries grouped by category.
- **Flow**:
  1. Fetches summaries from MongoDB.
  2. Returns summaries organized by category.

---

### 3. **POST** `/case`
- **Description**: Prepares a comprehensive case statement for O-1 visa applications.
- **Flow**:
  1. Collects grouped summaries from the database.
  2. Generates a detailed case statement via OpenAI GPT.
  3. Stores the case statement in MongoDB for future use.

---

### 4. **GET** `/case/latest`
- **Description**: Retrieves the most recent case statement.
- **Flow**:
  1. Queries MongoDB for the latest case statement.
  2. Returns the details of the case.

---

### 5. **GET** `/case/latest/download`
- **Description**: Downloads the most recent case statement as a PDF.
- **Flow**:
  1. Fetches the latest case statement from MongoDB.
  2. Converts the statement to a PDF using FPDF.
  3. Returns the PDF file to the client.

---

## **Deployment**
- **GitHub Repository**: [Migrately-RAG Repository](https://github.com/dev-mzain/Migrately-RAG)
- **Deployed Endpoint**: [Koyeb Deployment](https://concerned-carine-algorythm-27f8c324.koyeb.app)

---

## **Setup and Installation**
### Prerequisites
- Python 3.8 or higher
- MongoDB instance
- Access to Pinecone API and OpenAI GPT API

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/dev-mzain/Migrately-RAG.git
   cd Migrately-RAG
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Create a `.env` file in the project root with the following:
     ```
     DATABASE_URL=<your_mongodb_uri>
     PINECONE_KEY=<your_pinecone_api_key>
     OPENAI_API_KEY=<your_openai_api_key>
     ```
4. Run the application:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
