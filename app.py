from flask import Flask, request, render_template, redirect, url_for, flash
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = "your_secret_key"

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Route to display the upload form
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the POST request has the file part
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)

    file = request.files['file']

    # Check if a file was selected
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    # Ensure the file is a PDF or DOCX
    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        flash(f'File {file.filename} uploaded successfully', 'success')
        return redirect(url_for('upload_form'))
    else:
        # Invalid file format - display a bold message
        flash(f'<b> {file.filename} Invalid file format. Only PDF and DOCX are allowed.</b>', 'error')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
