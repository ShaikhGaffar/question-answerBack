from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pdfminer.high_level import extract_text
from transformers import pipeline
from docquery import document, pipeline as doc_pipeline

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
qa_pipeline = pipeline("question-answering")
doc_qa_pipeline = doc_pipeline('document-question-answering')

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def find_answer_in_text(question, text):
    # Use the question-answering model to get the answer
    # print('answer',text)
    result = qa_pipeline(question=question, context=text)

    # Extract and return the answer
    return result["answer"]

def find_answer_in_document(question, document_context):
    return doc_qa_pipeline(question=question, **document_context)

@app.route('/query', methods=['POST'])
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

        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        # print("Extracted text from PDF:", text)  # Debug print statement

        # Load document for docquery
        doc = document.load_document(file_path)
        print('doc',doc_pipeline)
        # Find answer in the extracted text
        answer_from_text = find_answer_in_text(question, text)
        
        # Find answer in the document
        answer_from_doc = find_answer_in_document(question, doc.context)
        
        # Delete the uploaded file after processing
        os.remove(file_path)

        return jsonify({'question': question, 'answer': answer_from_doc})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Set a secret key for secure session management
    # Define the upload folder
    app.config['UPLOAD_FOLDER'] = 'uploads'
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
