# Python libraries
import json, sqlite3
# Site-packages
from flask import Flask, jsonify

# Define the application as an instance of Flask
app=Flask(__name__)

# Define the sqlite database file
DATABASE = 'movie.sqlite'

@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    # Define the appropriate query
    query =  '''SELECT original_title, director_id
                FROM movies
                LIMIT 10;'''
    # query = 'SELECT original_title FROM movies'
    
    # Send the query to the execute_query function
    result = execute_query(query)
    # Jsonify the results as demanded
    return jsonify(result)

@app.route('/api/directors', methods=['GET'])
def get_all_directors():
    # Define the appropriate query
    query='SELECT name FROM directors'
    # Send the query to the execute_query function
    result=execute_query(query)
    # Jsonify the results
    json_data = json.dumps(result, indent=4)

    return json_data
    # return jsonify(result)

def execute_query(query):
    # Connect to the database
    connection = sqlite3.connect(DATABASE)
    # Define the curser
    cursor = connection.cursor()
    # Ececute the query
    cursor.execute(query)
    if query.lower().startswith('select'):
        # Fetch the query results as a list of dictionaries
        columns = [column[0] for column in cursor.description]
        # Jsonify the result
        query_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close() # best practice
        return query_results

if __name__ == '__main__':
    app.run(debug=True)



    





