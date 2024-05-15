import os
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from urllib.parse import unquote
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def list_subfolders(startpath):
    """List all subfolders in the given directory path."""
    subfolders = [f for f in os.listdir(startpath) if os.path.isdir(os.path.join(startpath, f))]
    return subfolders

def list_files(startpath):
    """List all files in the given directory path."""
    files = [f for f in os.listdir(startpath) if os.path.isfile(os.path.join(startpath, f))]
    return files

@app.route('/')
def index():
    """Render the main page with a list of subfolders from a predefined path."""
    root_path = r'C:\Users\JannisReufsteck\Documents'
    immediate_subfolders = list_subfolders(root_path)
    return render_template('index.html', immediate_subfolders=immediate_subfolders)

@app.route('/subfolders', methods=['POST'])
def get_subfolders():
    """Return subfolders and files of a given directory path from POST request."""
    folder_path = request.json['path']
    base_path = r'C:\Users\JannisReufsteck\Documents'
    folder_path = unquote(folder_path)
    full_path = os.path.join(base_path, folder_path)
    subfolders = list_subfolders(full_path)
    files = list_files(full_path)
    return jsonify({'subfolders': subfolders, 'files': files})

@app.route('/files/<path:filename>')
def files(filename):
    """Serve files from a specified path, handling various file types and errors."""
    base_path = r'C:\Users\JannisReufsteck\Documents'
    filename = unquote(filename)
    file_path = os.path.join(base_path, filename)

    logging.info(f"Attempting to access file: {file_path}")
    if not os.path.exists(file_path):
        logging.error("File not found at the path.")
        return jsonify({"error": "File not found"}), 404

    try:
        response = send_from_directory(directory=base_path, filename=filename, as_attachment=True)
        logging.info("File sent successfully.")
        return response
    except Exception as e:
        logging.critical(f"An error occurred when trying to send the file: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
