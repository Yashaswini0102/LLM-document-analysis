import os
import pytest
import json
from app import app, insert_metadata, preprocess_text

# Testing configuration
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'test_uploads/'  # Use a separate folder for test uploads
    client = app.test_client()

    # Create the upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    yield client

    # Cleanup after tests
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        os.rmdir(app.config['UPLOAD_FOLDER'])

# Mock DB function
def mock_insert_metadata(metadata, tokens):
    # Simulate successful metadata insert by doing nothing
    print(f"Mock insert metadata: {metadata}, Tokens: {tokens}")

# Test uploading a valid DOCX file
def test_upload_docx(client, monkeypatch):
    # Mock database insert function to prevent actual DB interaction during tests
    monkeypatch.setattr('app.insert_metadata', mock_insert_metadata)

    data = {
        'file': (open('test_files/sample.docx', 'rb'), 'sample.docx')
    }
    response = client.post('/upload', content_type='multipart/form-data', data=data)

    assert response.status_code == 200
    assert b"File uploaded and processed successfully!" in response.data

# Test uploading a valid PDF file
def test_upload_pdf(client, monkeypatch):
    monkeypatch.setattr('app.insert_metadata', mock_insert_metadata)

    file_path = 'test_files/sample.pdf'  # Ensure the path is correct
    with open(file_path, 'rb') as file:
        data = {'file': (file, 'sample.pdf')}
        response = client.post('/upload', content_type='multipart/form-data', data=data)

    assert response.status_code == 200
    assert b"File uploaded and processed successfully!" in response.data


# Test preprocessing function
def test_preprocess_text():
    sample_text = "This is a test document. Testing stopwords removal!"
    tokens = preprocess_text(sample_text)
    assert "test" in tokens
    assert "document" in tokens
    assert "this" not in tokens  # "this" is a stop word, so it should not appear

# Test unsupported file format
def test_upload_unsupported_file(client):
    data = {
        'file': (open('test_files/sample.txt', 'rb'), 'sample.txt')
    }
    response = client.post('/upload', content_type='multipart/form-data', data=data)

    assert response.status_code == 200
    assert b"Error: Unsupported file format!" in response.data

# Test no file selected
def test_no_file_selected(client):
    response = client.post('/upload', content_type='multipart/form-data', data={})

    # Debugging print to check response
    print(response.data)

    # Check status code
    assert response.status_code == 200

    # Check if the actual error message is present in the response
    assert b"No file part in the request" in response.data

# Test file not in request
def test_no_file_in_request(client):
    data = {'non_file_field': 'some_data'}
    response = client.post('/upload', content_type='multipart/form-data', data=data)

    assert response.status_code == 200
    assert b"No file part in the request" in response.data