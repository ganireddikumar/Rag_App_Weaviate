# RAG Application

A Retrieval Augmented Generation (RAG) application that allows users to upload documents, ask questions about them, and receive contextually relevant answers using advanced AI technologies.

## Features

- Document upload support for PDF and DOCX files
- Document processing and chunking with RecursiveCharacterTextSplitter
- Vector storage using Weaviate for efficient semantic search
- Question answering using Llama 3.3-70B-Instruct-Turbo via Together.ai
- Conversation history management with MySQL
- Modern React-based web interface with Material-UI
- Docker containerization for easy deployment
- Nginx reverse proxy for frontend serving

## Technical Architecture

### Backend (Python/Flask)
- Flask for RESTful API development
- LangChain for RAG implementation
- Weaviate for vector storage and semantic search
- MySQL for conversation and document storage
- Together.ai API for LLM access
- Document processing with PyPDF and python-docx
- CORS support for frontend communication

### Frontend (React)
- React with Material-UI components
- React Router for navigation
- Axios for API communication
- Nginx for serving static files
- Responsive design with Material-UI theming

### Database Schema
- `documents`: Stores uploaded document metadata
- `document_chunks`: Stores processed document chunks
- `conversations`: Stores Q&A history

## Process Flow

1. **Document Upload & Processing**
   - User uploads PDF/DOCX file
   - Backend processes document using appropriate parser
   - Text is split into chunks using RecursiveCharacterTextSplitter
   - Chunks are stored in MySQL and Weaviate

2. **Question Answering**
   - User selects document and asks question
   - Question is embedded using Together.ai embeddings
   - Weaviate performs semantic search to find relevant chunks
   - Context is provided to Llama model for answer generation
   - Conversation is stored in MySQL

3. **Vector Search**
   - Uses Weaviate's near_vector search
   - Configurable similarity threshold (0.7)
   - Returns top 3 most relevant chunks
   - Maintains document flow through chunk indexing

## Setup Instructions

### Using Docker (Recommended)
1. Clone the repository
2. Create `.env` file with required credentials:
   ```
   WEAVIATE_URL=your_weaviate_url
   WEAVIATE_API_KEY=your_weaviate_key
   TOGETHER_API_KEY=your_together_key
   MYSQL_HOST=mysql
   MYSQL_USER=your_mysql_user
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=ragdb
   ```
3. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Manual Setup
1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up MySQL database using `init-db.sql`
5. Configure environment variables in `.env`
6. Run the application:
   ```bash
   python app.py
   ```

## API Endpoints

- `POST /api/upload`: Upload and process documents
- `POST /api/chat`: Send questions and receive AI-generated answers
- `GET /api/conversations`: Retrieve conversation history
- `GET /api/documents`: List uploaded documents
- `POST /api/clear-chat-history`: Clear session chat history

## Environment Variables

Required environment variables:
- `WEAVIATE_URL`: Weaviate instance URL
- `WEAVIATE_API_KEY`: Weaviate API key
- `TOGETHER_API_KEY`: Together.ai API key
- `MYSQL_HOST`: MySQL host
- `MYSQL_PORT`: MySQL port (default: 3306)
- `MYSQL_USER`: MySQL username
- `MYSQL_PASSWORD`: MySQL password
- `MYSQL_DB`: MySQL database name
- `FLASK_SECRET_KEY`: Flask session secret key

## Vector Database Selection

Weaviate was chosen as the vector database for the following reasons:
- Cloud-native architecture with managed service
- Excellent scalability and performance
- Built-in support for text2vec-contextionary
- Simple integration with LangChain
- Free tier available for development
- Strong community support
- Efficient near_vector search capabilities
- Support for metadata filtering

## Dependencies

### Backend
- Flask and Flask-CORS
- LangChain and related packages
- Weaviate client
- MySQL connector
- Document processing libraries (PyPDF, python-docx)
- Together.ai integration

### Frontend
- React and React Router
- Material-UI components
- Axios for API calls
- Nginx for serving static files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 
