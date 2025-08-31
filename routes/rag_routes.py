from flask import Blueprint, request, jsonify
from services.rag_service import rag_service
import logging
import os
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

@rag_bp.route('/query', methods=['POST'])
def query_rag():
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question or not question.strip():
            return jsonify({"error": "Question is required"}), 400
            
        answer = rag_service.query(question)
        return jsonify({
            "question": question,
            "answer": answer,
            "has_knowledge": rag_service.has_documents()
        })
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@rag_bp.route('/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400
            
        # Save file
        filename = secure_filename(file.filename)
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Process file
        success = rag_service.load_document_from_file(filepath)
        
        if success:
            return jsonify({
                "message": "File uploaded and processed successfully",
                "filename": filename
            })
        return jsonify({"error": "Failed to process file"}), 500
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": "Internal server error"}), 500

def init_rag_routes(app):
    app.register_blueprint(rag_bp)