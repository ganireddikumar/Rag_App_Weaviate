import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import weaviate
from weaviate.classes.query import Filter
from weaviate.classes.init import Auth
from weaviate.classes.config import Property, DataType, Configure, Tokenization
from langchain_together import TogetherEmbeddings
from langchain_together import Together
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Weaviate
from pypdf import PdfReader
from docx import Document

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.secret_key = 'gani'

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Weaviate client
weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv('WEAVIATE_URL'),
    auth_credentials=Auth.api_key(os.getenv('WEAVIATE_API_KEY'))
)

# Initialize Together components
embeddings = TogetherEmbeddings(
    model="togethercomputer/m2-bert-80M-32k-retrieval",
    together_api_key=os.getenv('TOGETHER_API_KEY')
)

llm = Together(
    together_api_key=os.getenv('TOGETHER_API_KEY'),
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.1
)

# MySQL connection helper
def get_mysql_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
    except Error as e:
        print(f"MySQL Error: {e}")
        return None

# Document processing functions
def process_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf_reader.pages])

def process_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return splitter.split_text(text)

# Weaviate schema setup
def initialize_weaviate_schema():
    with weaviate_client:
        if not weaviate_client.collections.exists("DocumentChunks"):
            weaviate_client.collections.create(
                name="DocumentChunks",
                properties=[
                    {
                        "name": "document_id",
                        "data_type": DataType.TEXT,
                        "description": "The document identifier"
                    },
                    {
                        "name": "chunk",
                        "data_type": DataType.TEXT,
                        "description": "The text chunk content"
                    },
                    {
                        "name": "chunk_index",
                        "data_type": DataType.INT,
                        "description": "The index of the chunk in the document"
                    }
                ],
                vectorizer_config=None,
                description="Collection for storing document chunks"
            )

# API Endpoints
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    if not file.filename.lower().endswith(('.pdf', '.docx')):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process document
        if filename.endswith('.pdf'):
            text = process_pdf(file_path)
        else:
            text = process_docx(file_path)

        # Chunk text
        chunks = chunk_text(text)

        # Store in MySQL
        conn = get_mysql_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        try:
            # Insert document record
            cursor.execute(
                "INSERT INTO documents (filename, file_type) VALUES (%s, %s)",
                (filename, os.path.splitext(filename)[1])
            )
            document_id = cursor.lastrowid

            # Generate embeddings and store in Weaviate
            vectors = embeddings.embed_documents(chunks)
            
            with weaviate_client:
                collection = weaviate_client.collections.get("DocumentChunks")
                for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                    collection.data.insert(
                        properties={
                            "document_id": str(document_id),
                            "chunk": chunk,
                            "chunk_index": i
                        },
                        vector=vector
                    )

            # Store chunks in MySQL
            for i, chunk in enumerate(chunks):
                cursor.execute(
                    "INSERT INTO document_chunks (document_id, chunk_text, chunk_index) VALUES (%s, %s, %s)",
                    (document_id, chunk, i)
                )
            
            conn.commit()
            return jsonify({
                "message": "File processed successfully",
                "document_id": document_id,
                "chunk_count": len(chunks)
            })

        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import session
from datetime import datetime

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'question' not in data or 'document_id' not in data:
        return jsonify({"error": "Missing question or document_id"}), 400
    
    # Initialize session if not exists
    if 'chat_history' not in session:
        session['chat_history'] = []

    try:
        # Generate question embedding
        question_embedding = embeddings.embed_query(data['question'])

        # Search Weaviate
        with weaviate_client:
            collection = weaviate_client.collections.get("DocumentChunks")
            response = collection.query.near_vector(
                near_vector=question_embedding,
                distance=0.85,  # More lenient similarity threshold (changed from 0.7)
                limit=5,      # Increased number of chunks (changed from 3)
                filters=Filter.by_property("document_id").equal(str(data['document_id'])),
                return_properties=["chunk", "chunk_index"]
            )
            
            # Sort chunks by index to maintain document flow
            sorted_chunks = sorted(response.objects, key=lambda x: x.properties["chunk_index"])

        # Extract context from sorted chunks
        context = "\n\n".join([obj.properties["chunk"] for obj in sorted_chunks])
        
        # If no relevant context found
        if not context.strip():
            return jsonify({"answer": "I don't have enough information to answer that question."})

        # Generate response using Together.ai
        prompt = f"""You are a helpful AI assistant analyzing a document. Use the provided context to answer the question thoroughly and accurately. 
    
        Context: {context}
    
        Question: {data['question']}
        
        Instructions:
        1. Use the information from the provided context to answer the question
        2. If you can make a reasonable inference from the context, you may do so while indicating it's an inference
        3. If the context is partially relevant, provide what information you can and explain what's missing
        4. Only say "I don't have enough information" if the context is completely unrelated to the question
        5. Keep your answer clear and well-structured
        
        Answer: """
        
        answer = llm(prompt)

        # Store conversation
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO conversations (document_id, question, answer) VALUES (%s, %s, %s)",
                    (data['document_id'], data['question'], answer)
                )
                conn.commit()
            except Exception as e:
                print(f"Error storing conversation: {str(e)}")
            finally:
                cursor.close()
                conn.close()

        # Store conversation in session
        chat_entry = {
            'document_id': data['document_id'],
            'question': data['question'],
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        }
        session['chat_history'].append(chat_entry)
        
        return jsonify({
            "answer": answer,
            "chat_history": session['chat_history']
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    conn = get_mysql_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM documents ORDER BY upload_date DESC")
        documents = cursor.fetchall()
        return jsonify(documents)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    document_id = request.args.get('document_id')
    if not document_id:
        return jsonify({"error": "Missing document_id parameter"}), 400

    conn = get_mysql_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM conversations WHERE document_id = %s ORDER BY timestamp DESC",
            (document_id,)
        )
        conversations = cursor.fetchall()
        return jsonify(conversations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the RAG Application API'})

@app.route('/api/clear-chat-history', methods=['POST'])
def clear_chat_history():
    if 'chat_history' in session:
        session.pop('chat_history')
    return jsonify({"message": "Chat history cleared successfully"})

if __name__ == '__main__':
    initialize_weaviate_schema()
    app.run(host='0.0.0.0', port=5000, debug=True)
    
