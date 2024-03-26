from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import openai
import json
from difflib import get_close_matches

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "users_db"

mysql = MySQL(app)

str1 = 'sk-6DurzFcba69Gqq8KkZeAT3B'
str2 = 'lbkFJYWeBEwHHM'
str3 = 'JVnBzt79unM'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    chatgpt_input = request.form['chatgpt']  # Get user input from the form
    
    # Initialize OpenAI
    openai.api_key = str1 + str2 + str3
    
    # Send user input to OpenAI for completion
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": chatgpt_input}])
    chatgpt_output = completion.choices[0].message.content
    
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

    return render_template('index.html', chatgpt_input=chatgpt_input, chatgpt_output=chatgpt_output, userDetails=userDetails)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
