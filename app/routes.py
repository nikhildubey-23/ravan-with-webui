from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import re
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Use environment variable or default value
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Set up logging
logging.basicConfig(level=logging.INFO)

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def create_database():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 question TEXT, 
                 answer TEXT, 
                 timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_to_history(question, answer):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO user_history (question, answer, timestamp) VALUES (?, ?, ?)", (question, answer, timestamp))
    conn.commit()
    conn.close()

def view_history():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM user_history")
    rows = c.fetchall()
    conn.close()
    return rows

def clear_history():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM user_history")
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if not os.path.exists(DATABASE_PATH):
        create_database()

    output = None
    output_language = "plaintext"  # Default language
    if request.method == 'POST':
        try:
            user_input = request.form['user_input']
            llm = ChatGroq(
                temperature=0, 
                groq_api_key=GROQ_API_KEY, 
                model_name="deepseek-r1-distill-llama-70b"
            )
            prompt_template = create_prompt()
            chain_extract = prompt_template | llm 
            res = chain_extract.invoke(user_input)
            output = re.sub(r'<think>.*?</think>', '', res.content, flags=re.DOTALL).strip()  # Remove <think> tags and their content

            # Preprocess the output to replace ** with <h2> tags only outside of code blocks
            def replace_double_asterisks(match):
                text = match.group(0)
                return re.sub(r'\*\*(.*?)\*\*', r'<h2>\1</h2>', text)

            output = re.sub(r'(?s)(```.*?```|[^`]+)', replace_double_asterisks, output)
            output = re.sub(r'```(\w+)\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', output, flags=re.DOTALL)  # Wrap code blocks in <pre><code> tags

            save_to_history(user_input, output)
            flash(output)
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            flash("An error occurred while processing your request. Please try again.")
            return jsonify({"error": str(e)}), 500

    history = view_history()
    return render_template('index.html', history=history, output=output, output_language=output_language)

@app.route('/view_history', methods=['GET'])
def view_history_page():
    history = view_history()
    return render_template('history.html', history=history)

@app.route('/clear_history', methods=['POST'])
def clear():
    clear_history()
    flash("History cleared successfully!")
    return redirect(url_for('index'))

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/reachout', methods=['GET'])
def reachout():
    return render_template('reachout.html')

def create_prompt():
    prompt_template = """
Ravan Offensive Security AI Assistant:
You are an expert in cybersecurity and can provide security solutions to users.
You can write code in Python and other languages.
You can understand English languages.
You are a very good web developer and code designer.
Your goal is to assist users with their cybersecurity needs.
You provide answer only for the asked question no need of extra information.
Your developer name is Ravan
Please respond to the following prompt:
{input}
"""
    return PromptTemplate.from_template(prompt_template)

if __name__ == '__main__':
    app.run(debug=True)