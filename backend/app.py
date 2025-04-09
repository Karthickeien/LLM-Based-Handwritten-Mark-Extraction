from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import traceback
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import tempfile
from utils.image_processor import ImageProcessor
from utils.excel_handler import ExcelHandler

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure uploads folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit uploads to 16MB

# Initialize utility classes
GOOGLE_API_KEY = os.environ.get('AIzaSyB7nO0uXJylUWQUA6iBkc_JsvdAm_P3BA0')
if not GOOGLE_API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable not set")

image_processor = ImageProcessor(api_key=GOOGLE_API_KEY)
excel_handler = ExcelHandler()

@app.route('/api/process-image', methods=['POST'])
def process_image():
    """API endpoint to process uploaded marksheet images"""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process the image with the ImageProcessor
        results = image_processor.extract_data_from_image(file_path)
        
        # Clean up the uploaded file
        os.remove(file_path)
        
        return jsonify(results)
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        print(traceback.format_exc())
        
        # Clean up on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            
        return jsonify({"error": f"Error processing the image: {str(e)}"}), 500

@app.route('/api/export-csv', methods=['POST'])
def export_csv():
    """API endpoint to generate CSV from extracted data"""
    try:
        # Get data from request
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Create CSV content
        csv_content = excel_handler.create_csv_from_data(data)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w') as temp_file:
            temp_file.write(csv_content)
            temp_path = temp_file.name
        
        # Send the file
        return send_file(
            temp_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='marksheet_results.csv'
        )
    
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Error exporting to CSV: {str(e)}"}), 500

@app.route('/api/export-excel', methods=['POST'])
def export_excel():
    """API endpoint to generate Excel file from extracted data"""
    try:
        # Get data from request
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp:
            temp_path = temp.name
        
        # Export data to Excel
        excel_path = excel_handler.export_to_excel(data, temp_path)
        
        # Send the file
        return send_file(
            excel_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='marksheet_results.xlsx'
        )
    
    except Exception as e:
        print(f"Error exporting to Excel: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Error exporting to Excel: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "message": "Service is running"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)