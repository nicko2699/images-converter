from flask import Flask, render_template, request, send_from_directory
import requests
import os
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', uploaded_image=None, vectorized_image=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_file(file.filename):
        filepath = save_uploaded_file(file)
        response = vectorize_image(filepath)
        
        if response.status_code == requests.codes.ok:
            save_vectorized_image(response)
            uploaded_image = f'/static/uploaded_image.jpg?{time.time()}'
            vectorized_image = '/static/result.svg?{time.time()}'
            return render_template('index.html', uploaded_image=uploaded_image, vectorized_image=vectorized_image)
        else:
            return f"Error: {response.status_code}, {response.text}"

def save_uploaded_file(file):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    file.save(filepath)
    return filepath

def vectorize_image(filepath):
    return requests.post(
        'https://es.vectorizer.ai/api/v1/vectorize',
        files={'image': open(filepath, 'rb')},
        data={'mode': 'test'},
        auth=('vksq8h4q6tz2avq', '1fe1mta5v9lksq20otsk34vcq7q91elqlcigg9bf0ghom118955a')
    )

def save_vectorized_image(response):
    with open('static/result.svg', 'wb') as out:
        out.write(response.content)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

