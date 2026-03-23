from flask import Flask, request
import git
app = Flask(__name__)
@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('home/oscar1234/Eksamensprojekt-Informatik')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

@app.route('/')
def hello_world():
    return 'Hello from Flask!'
