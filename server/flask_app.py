from flask import Flask
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
