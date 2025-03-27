# RAG Application

A Retrieval Augmented Generation (RAG) application that allows users to upload documents, ask questions about them, and receive contextually relevant answers.

## Features

- Document upload support for PDF and DOCX files
- Document processing and chunking
- Vector storage using Weaviate
- Question answering using Llama 3.* via Together.ai
- Conversation history management with MySQL
- Simple and intuitive web interface

## Technical Architecture

### Backend
- Python with Flask for API development
- LangChain for RAG implementation
- Weaviate for vector storage
- MySQL for conversation storage
- Together.ai API for LLM access

### Frontend
- React-based web interface
- Document upload view
- Chat interface with conversation history

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up MySQL database:
   ```sql
   CREATE DATABASE ragdb;
   ```
5. Configure environment variables in `.env` file
6. Run the application:
   ```bash
   python app.py
   ```

## Vector Database Selection

Weaviate was chosen as the vector database for the following reasons:
- Cloud-native architecture with managed service
- Excellent scalability and performance
- Built-in support for text2vec-contextionary
- Simple integration with LangChain
- Free tier available for development
- Strong community support

## API Endpoints

- `POST /api/upload`: Upload documents
- `POST /api/chat`: Send questions and receive answers
- `GET /api/conversations`: Retrieve conversation history
- `GET /api/documents`: List uploaded documents

## Environment Variables

Required environment variables:
- `WEAVIATE_URL`: Weaviate instance URL
- `WEAVIATE_API_KEY`: Weaviate API key
- `TOGETHER_API_KEY`: Together.ai API key
- `MYSQL_HOST`: MySQL host
- `MYSQL_PORT`: MySQL port
- `MYSQL_USER`: MySQL username
- `MYSQL_PASSWORD`: MySQL password
- `MYSQL_DB`: MySQL database name 