from flask import Flask, request, jsonify,send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pdfminer.high_level import extract_text
from docquery import pipeline, document
import threading
import time

app = Flask(__name__,static_folder='./build/static')
CORS(app, resources={r"/*": {"origins": "*"}})
# Initialize the document-question-answering pipeline with donut model
doc_qa_pipeline = pipeline('document-question-answering')

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def find_answer_in_document(question, document_context):
    try:
        # Call the pipeline to get the answers
        results = doc_qa_pipeline(question=question, **document_context)
        print(results)  # Print results here
        # Collect all answers from the results
        answers = []
        for result in results:
            if 'answer' in result:
                answers.append(result['answer'])
        if answers:
            # Concatenate all answers into a single string
            full_answer = ' '.join(answers)
            return full_answer
        else:
            return "Answer not found in document"
    except Exception as e:
        return str(e)

def delete_file_after_delay(file_path, delay):
    time.sleep(delay)
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")
@app.route('/')
def index():
    return send_from_directory('./build', 'index.html')
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('./build/static', path)
@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory('./build', 'favicon.ico')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('./build', 'manifest.json')
@app.route('/logo192.png')
def logo_192():
    return send_from_directory('./build', 'logo192.png')

@app.route('/queryTest')
def test():
        print('asdfasdf sdf sdf adsff ')
        return jsonify({'question': 'question', 'answer': 'answer_from_doc'})

@app.route('/api/query', methods=['POST'])
def query_document():
    try:
        question = request.form['question']
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400
        # Save the uploaded file securely
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Start a thread to delete the file after 2 minutes
        deletion_thread = threading.Thread(target=delete_file_after_delay, args=(file_path, 3600))
        deletion_thread.start()
        # Load document for docquery
        doc = document.load_document(file_path)
        # Find answer in the document
        answer_from_doc = find_answer_in_document(question, doc.context)
        return jsonify({'question': question, 'answer': answer_from_doc})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Set a secret key for secure session management
    app.secret_key = 'your_secret_key_here'
    # Define the upload folder
    app.config['UPLOAD_FOLDER'] = 'uploads'
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=7000)
