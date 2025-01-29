from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
    
    with app.app_context():
        from . import routes

    return app

app = create_app()