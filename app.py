import os
import json
import spacy
import pytesseract
import psycopg2
from PIL import Image
from tika import parser
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from docx import Document

# Initialize the Flask app
app = Flask(__name__)

# Set the upload folder path
app.config['UPLOAD_FOLDER'] = 'uploads/'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load the SpaCy model
nlp = spacy.load('en_core_web_sm')

# PostgreSQL database configuration
DB_CONFIG = {
    'dbname': 'metadata_db',
    'user': 'yashaswini',
    'password': 'Yashu@2003',
    'host': 'localhost',
    'port': '5432'
}

# Test PostgreSQL connection
def test_db_connection():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        connection.close()
        print("Database connection successful.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise e

# Call test_db_connection at startup to ensure DB is reachable
test_db_connection()

# Function to save uploaded files
def save_upload_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return filepath

# Function to read DOCX files
def read_docx(filepath):
    doc = Document(filepath)
    full_text = [para.text for para in doc.paragraphs]
    return '\n'.join(full_text)

# Function to extract text using Tika or OCR
def extract_text(file_path):
    if file_path.endswith('.pdf') or file_path.endswith('.docx'):
        parsed = parser.from_file(file_path)
        return parsed.get('content', '')
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)
    else:
        raise ValueError('Unsupported file format!')

# Function to preprocess text
def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if not token.is_stop and token.is_alpha]
    return tokens

# Function to extract metadata
def extract_metadata(filepath, content):
    metadata = {
        'title': os.path.basename(filepath),
        'author': 'Unknown Author',  # You can add logic to extract author from the document if possible
        'doc_type': os.path.splitext(filepath)[1].lower(),
        'content_length': len(content),
    }
    return metadata

# Function to insert metadata into PostgreSQL database
def insert_metadata(metadata, tokens):
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Insert metadata query
        insert_query = """
        INSERT INTO document_metadata (title, author, doc_type, content_length, tokens)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            metadata['title'],
            metadata['author'],
            metadata['doc_type'],
            metadata['content_length'],
            json.dumps(tokens)  # Ensure tokens are serialized to JSON
        ))

        connection.commit()
        print("Metadata inserted successfully.")  # Logging for successful insert

    except psycopg2.DatabaseError as e:
        connection.rollback()  # Rollback in case of error
        print(f"Error inserting data into the database: {e}")  # Logging errors
        raise e  # Rethrow the error to be caught in the outer try-except block

    finally:
        cursor.close()
        connection.close()

# Flask Routes

# Home route
@app.route('/')
def upload_form():
    return render_template('upload.html')

from flask import Flask, render_template, request

# Upload and process file route
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', message="No file part in the request")

        file = request.files['file']

        if file.filename == '':
            return render_template('upload.html', message="No file selected")

        try:
            # Save file and get its path
            file_path = save_upload_file(file)

            # Extract text
            document_text = extract_text(file_path)

            # Preprocess the text
            processed_tokens = preprocess_text(document_text)

            # Extract metadata
            metadata = extract_metadata(file_path, document_text)

            # Insert metadata into PostgreSQL
            insert_metadata(metadata, processed_tokens)

            # Return the form with a success message
            return render_template('upload.html', message="File uploaded and processed successfully!")

        except Exception as e:
            print(f"Error: {e}")
            return render_template('upload.html', message=f"Error: {str(e)}")

    # If it's a GET request, just render the upload form
    return render_template('upload.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
