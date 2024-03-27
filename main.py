from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import json
from difflib import get_close_matches

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "users_db"

mysql = MySQL(app)

def load_knowledge_base(file_path: str) -> str:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches: list = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]
    return None

def get_link_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base.get("questions", []):
        if q.get("question") == question:
            return q.get("link")  # Return the link if it exists, otherwise return None
    return None

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/submit', methods=['GET', 'POST'])
def chat_bot():
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')
    chatgpt_input = request.form['chatgpt']
    best_match = find_best_match(chatgpt_input, [q["question"] for q in knowledge_base["questions"]])

    if best_match:
        answer = get_answer_for_question(best_match, knowledge_base)
        link = get_link_for_question(best_match, knowledge_base)
        if link:
            chatgpt_output = f'{answer} Link: {link}'
        else:
            chatgpt_output = f'{answer}' # If link is missing or not defined
    else:
        chatgpt_output = 'I don\'t know the answer.'

    # Store user input and model output in the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users_gpt (input, output) VALUES (%s, %s)", (chatgpt_input, chatgpt_output))
    mysql.connection.commit()
    cur.close()

    # Fetch all data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users_gpt ORDER BY id DESC LIMIT 5")
    userDetails = cur.fetchall()
    cur.close()

    return render_template('index2.html', chatgpt_input=chatgpt_input, chatgpt_output=chatgpt_output, userDetails=userDetails)
            #new_answer: str = input('Type the answer or "skip" to skip: ')

            #if new_answer.lower() != 'skip':
                #knowledge_base["questions"].append({"question": user_input, "answer": new_answer})
                #save_knowledge_base('knowledge_base.json', knowledge_base)

if __name__ == "__main__":
    #chat_bot()
    app.run(debug=False, host='0.0.0.0')
