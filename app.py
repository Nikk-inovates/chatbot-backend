from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": "chatbot-db",  # Change if your database name is different
    "user": "postgres",
    "password": "9926",  # Update if your password is different
    "host": "localhost",
    "port": "5432"
}

# Function to connect to PostgreSQL
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

# Fetch bot response from the database
def get_bot_response(user_input):
    """Fetches the bot response for a given user input from the chatbot_dialogs table."""
    try:
        conn = get_db_connection()
        if conn is None:
            return "Error: Unable to connect to the database."
        
        cur = conn.cursor()
        
        # Fetch bot response where user_text matches input
        cur.execute("SELECT bot_text FROM chatbot_dialogs WHERE LOWER(TRIM(user_text)) = LOWER(TRIM(%s))", (user_input,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return result[0]  # Return bot response from database
        else:
            return "I don't understand that yet. Try another question!"  # Default response if not found

    except Exception as e:
        print(f"Database query error: {str(e)}")
        return "Error fetching response from the database."

# Chatbot API route
@app.route('/chat', methods=['POST'])
def chat():
    """Receives user input and returns the bot's response from the database."""
    try:
        data = request.get_json()
        user_input = data.get("user_input", "").strip()  # Remove extra spaces

        if not user_input:
            return jsonify({"error": "User input is required"}), 400

        # Get bot response from database
        bot_response = get_bot_response(user_input)

        return jsonify({"bot_response": bot_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Home route
@app.route('/')
def home():
    return "Chatbot API is running!"

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)  # Change 8000 to your desired port
