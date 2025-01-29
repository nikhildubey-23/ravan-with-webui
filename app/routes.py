from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

def create_database(email):
    conn = sqlite3.connect(f'{email}.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 question TEXT, 
                 answer TEXT, 
                 timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_to_history(email, question, answer):
    conn = sqlite3.connect(f'{email}.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO user_history (question, answer, timestamp) VALUES (?, ?, ?)", (question, answer, timestamp))
    conn.commit()
    conn.close()

def view_history(email):
    conn = sqlite3.connect(f'{email}.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_history")
    rows = c.fetchall()
    conn.close()
    return rows

def clear_history(email):
    conn = sqlite3.connect(f'{email}.db')
    c = conn.cursor()
    c.execute("DELETE FROM user_history")
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    email = "default_user"
    if not os.path.exists(f'{email}.db'):
        create_database(email)

    output = None
    output_language = "plaintext"  # Default language
    if request.method == 'POST':
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

        save_to_history(email, user_input, output)
        flash(output)

    history = view_history(email)
    return render_template('index.html', history=history, output=output, output_language=output_language)

@app.route('/view_history', methods=['GET'])
def view_history_page():
    email = "default_user"
    history = view_history(email)
    return render_template('history.html', history=history)

@app.route('/clear_history', methods=['POST'])
def clear():
    email = "default_user"
    clear_history(email)
    flash("History cleared successfully!")
    return redirect(url_for('index'))

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