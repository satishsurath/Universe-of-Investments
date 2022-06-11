import sys, os

INTERP = os.path.join(os.environ['HOME'], 'trade.runningdigitally.com', 'venv2', 'bin', 'python3')


if os.environ['HOME'] != '/home/dh_nm8gqc':
    from dotenv import load_dotenv 
    load_dotenv()
    if (os.environ.get('INTERP')):
        INTERP = os.environ.get('INTERP')

if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from flask import Flask
application = Flask(__name__)

###### commenting this section to now load 'app'
#@application.route('/')
#def index():
#    return 'Hello from Passenger (and Fintech Group 11), - Something awesome is brewing! Standby for more updates!'


sys.path.append('app')
from app import app as application



from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}