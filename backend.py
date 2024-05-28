import os
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory, Response
from urllib.parse import unquote
import mimetypes

# Configure logging
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
    root_path = r'C:\Users\JannisReufsteck\Desktop\bootstrap-5.3.3-dist'
    immediate_subfolders = list_subfolders(root_path)
    return render_template('index.html', immediate_subfolders=immediate_subfolders)

@app.route('/subfolders', methods=['POST'])
def get_subfolders():
    """Return subfolders and files of a given directory path from POST request."""
    folder_path = request.json['path']
    base_path = r'C:\Users\JannisReufsteck\Desktop\bootstrap-5.3.3-dist'
    folder_path = unquote(folder_path)
    full_path = os.path.join(base_path, folder_path)
    subfolders = list_subfolders(full_path)
    files = list_files(full_path)
    return jsonify({'subfolders': subfolders, 'files': files})

@app.route('/files/<path:filename>')
def files(filename):
    """Serve files from a specified path, handling various file types and errors."""
    base_path = r'C:\Users\JannisReufsteck\Desktop\bootstrap-5.3.3-dist'
    decoded_filename = unquote(filename)  # Decode URL-encoded strings

    # Construct the full path using the decoded filename
    file_path = os.path.join(base_path, decoded_filename)

    logging.info(f"Attempting to access file: {file_path}")
    logging.info(f"Decoded filename: {decoded_filename}")

    if not os.path.exists(file_path):
        logging.error("File not found at the path.")
        return jsonify({"error": "File not found"}), 404

    mime_type, _ = mimetypes.guess_type(file_path)
    logging.info(f"Detected MIME type: {mime_type}")

    try:
        # Serve the file for download
        directory = os.path.dirname(file_path)
        file_basename = os.path.basename(file_path)
        response = send_from_directory(directory=directory, path=file_basename, as_attachment=True)
        logging.info("File sent successfully.")
        return response
    except Exception as e:
        logging.error(f"An error occurred when trying to send the file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/viewfile/<path:filename>')
def view_file(filename):
    """Render the content of a file for inline viewing."""
    base_path = r'C:\Users\JannisReufsteck\Desktop\bootstrap-5.3.3-dist'
    decoded_filename = unquote(filename)  # Decode URL-encoded strings

    # Construct the full path using the decoded filename
    file_path = os.path.join(base_path, decoded_filename)

    if not os.path.exists(file_path):
        logging.error("File not found at the path.")
        return jsonify({"error": "File not found"}), 404

    mime_type, _ = mimetypes.guess_type(file_path)
    logging.info(f"Detected MIME type: {mime_type}")

    try:
        # Check if the MIME type is suitable for inline viewing
        if mime_type and (mime_type.startswith('text') or mime_type == 'application/json' or file_path.endswith(('.js', '.json', '.md'))):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return Response(content, mimetype='text/plain')
        elif mime_type and (mime_type == 'application/pdf' or mime_type.startswith('image') or mime_type.startswith('application/vnd.ms-powerpoint')):
            return send_from_directory(directory=os.path.dirname(file_path), path=os.path.basename(file_path), as_attachment=False)
        else:
            return render_template('view_file.html', filename=decoded_filename)
    except Exception as e:
        logging.error(f"An error occurred when trying to read the file: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
