# Flask Offensive Security AI Assistant

This project is a Flask web application that serves as an AI assistant for cybersecurity queries. It allows users to input questions, receive answers, and view their query history.

## Project Structure

```
flask-app
├── app
│   ├── __init__.py
│   ├── routes.py
│   ├── templates
│   │   └── index.html
│   └── static
├── .env
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd flask-app
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   Create a `.env` file in the root directory and add your `GROQ_API_KEY`:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

6. **Run the application:**

   ```
   export FLASK_APP=./app/routes.py
   flask run
   
   ```

## Usage

- Open your web browser and navigate to `http://127.0.0.1:5000`.
- Enter your question in the input field and click "Get Answer" to receive a response from the AI assistant.
- Use the "View History" button to see your previous queries and responses.
- Click "Clear History" to delete all saved queries.

## Dependencies

- Flask
- python-dotenv
- langchain_groq
- langchain_core
- pyperclip
- sqlite3

## License

This project is licensed under the MIT License. See the LICENSE file for more details.