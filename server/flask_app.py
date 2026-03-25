from flask import Flask, render_template, request
import os


app = Flask(__name__)
@app.route('/update_server')
def update():
    os.system('cd /home/oscar1234/Eksamensprojekt-Informatik && git pull')
    # Til at reload app
    os.system("touch /var/www/oscar1234_pythonanywhere_com_wsgi.py")
    return 'Updated and reloaded'

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/upload_form')
def upload_form():
    return render_template("upload_form.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'no file part'

    file = request.files['file']

    if file.filename == '':
        return 'no selected file'

    file.save(f'server/uploads/{file.filename}')

    return 'File uploaded successfully'




