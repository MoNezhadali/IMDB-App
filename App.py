# Python libraries
import sqlite3, time, json
# Site-packages
from flask import Flask, render_template, request, jsonify


app = Flask(__name__)

# Define the SQLite database file
DATABASE = 'movie.sqlite'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute_sql', methods=['POST'])
def execute_sql():
    query = request.form['query']
    result = execute_query(query)
    return jsonify(result)

def execute_query(query):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute(query)
    if query.lower().startswith('select'):
        result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close() # best practice
        connection.close()
        return {'data': result, 'columns': column_names}
    else:
        connection.commit()
        cursor.close()
        connection.close()
        return {'message': 'Query executed successfully.'}

if __name__ == '__main__':
    app.run(debug=True, port=8080)
