from flask import Flask
import os


app = Flask(__name__)
@app.route('/update_server')
def update():
    os.system('cd /home/oscar1234/Eksamensprojekt-Informatik && git pull')
    return 'Updated'

@app.route('/')
def hello_world():
    return 'Hello from Flask!'
