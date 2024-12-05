import logging
from pinecone import Pinecone, ServerlessSpec
import openai
from config import variables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pinecone with the API key
pc = Pinecone(api_key=variables.PINECONE_KEY)

# Define index name and dimensions
index_name = "o1-visa-docs"
dimension = 1536

# Create or connect to the Pinecone index
try:
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric='euclidean',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    index = pc.Index(index_name)
    logger.info(f"Connected to Pinecone index: {index_name}")
except Exception as e:
    logger.error(f"Error initializing Pinecone: {e}")
    raise Exception("Failed to initialize Pinecone.")

def create_document_embedding(text: str):
    """
    Generate an embedding for the document using OpenAI's embedding API.
    """
    try:
        response = openai.Embedding.create(model="text-embedding-ada-002", input=text)
        return response['data'][0]['embedding']  # Ensure this returns a list, not a NumPy array
    except Exception as e:
        logger.error(f"Error generating embedding for the document: {e}")
        raise Exception("Failed to generate embedding.")

def add_document_to_index(text: str, metadata: dict):
    """
    Create an embedding and add the document to the Pinecone index.
    """
    try:
        embedding = create_document_embedding(text)
        index.upsert([{"id": metadata["chunk_id"], "values": embedding, "metadata": metadata}])
        logger.info(f"Document chunk {metadata['chunk_id']} added to Pinecone index.")
    except Exception as e:
        logger.error(f"Error adding document to Pinecone index: {e}")
        raise Exception("Failed to add document to Pinecone.")

def retrieve_relevant_chunks(query: str, file_name: str, top_k: int = 5):
    """
    Retrieve the most relevant chunks for a query from the Pinecone index.
    Restrict results to chunks belonging to the same document (by file_name).
    """
    try:
        query_embedding = create_document_embedding(query)
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"file_name": file_name}  # Filter by the file_name metadata
        )
        if "matches" in results:
            return [match["metadata"]["text"] for match in results["matches"]]
        else:
            logger.warning(f"No matches found for query: {query}")
            return []
    except Exception as e:
        logger.error(f"Error retrieving relevant chunks from Pinecone: {e}")
        raise Exception("Failed to retrieve relevant chunks.")

def summarize_document(file_text: str, metadata: dict):
    """
    Summarize a document using RAG principles.
    1. Embed and store the document chunks.
    2. Retrieve relevant chunks.
    3. Use GPT to summarize the chunks.
    """
    try:
        # Step 1: Split the document into chunks
        chunk_size = 250  # Adjust as needed
        chunks = [file_text[i:i+chunk_size] for i in range(0, len(file_text), chunk_size)]

        # Step 2: Embed and add each chunk to the index
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["text"] = chunk
            chunk_metadata["chunk_id"] = f"{metadata['file_name']}_chunk_{i}"
            add_document_to_index(chunk, chunk_metadata)

        # Step 3: Query the index to retrieve relevant chunks
        query = "Summarize this document."
        relevant_chunks = retrieve_relevant_chunks(query, metadata["file_name"])

        # Combine the retrieved chunks into one document to be summarized
        combined_text = " ".join(relevant_chunks)
        return combined_text
    except Exception as e:
        logger.error(f"Error summarizing document: {e}")
        raise Exception("Failed to summarize document.")
