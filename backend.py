import os
import re  
import mimetypes
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

def list_subfolders(startpath):
    subfolders = [f for f in os.listdir(startpath) if os.path.isdir(os.path.join(startpath, f))]
    return subfolders

def list_files(startpath):
    files = [f for f in os.listdir(startpath) if os.path.isfile(os.path.join(startpath, f))]
    return files

@app.route('/')
def index():
    root_path = r'C:\Users\JannisReufsteck\Documents'
    immediate_subfolders = list_subfolders(root_path)
    return render_template('index.html', immediate_subfolders=immediate_subfolders)

@app.route('/subfolders', methods=['POST'])
def get_subfolders():
    folder_path = request.json['path']
    base_path = r'C:\Users\JannisReufsteck\Documents'
    folder_path = re.sub(r'\s+', '', folder_path)  # remove whitespaces
    full_path = os.path.join(base_path, folder_path)
    subfolders = list_subfolders(full_path)
    files = list_files(full_path)
    return jsonify({'subfolders': subfolders, 'files': files})

@app.route('/files/<path:filename>')
def files(filename):
    base_path = r'C:\Users\JannisReufsteck\Documents'
    filename = secure_filename(filename)
    file_path = os.path.join(base_path, filename)
    mime_type, _ = mimetypes.guess_type(file_path)

    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            if 'text' in mime_type:
                file_content = file_content.decode('utf-8')
                return jsonify({'filename': filename, 'content': file_content, 'mime_type': mime_type})
            elif 'image' in mime_type and 'image/svg+xml' != mime_type:
                import base64
                file_content = base64.b64encode(file_content).decode('utf-8')
                return jsonify({'filename': filename, 'content': file_content, 'mime_type': mime_type})
            else:
                return send_from_directory(base_path, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
