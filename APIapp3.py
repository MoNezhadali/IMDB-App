# Python libraries
import os, json, sqlite3
# Site-packages
from flask import Flask, jsonify, request

# Define the application as an instance of Flask
app = Flask(__name__)

# Define the sqlite database file
DATABASE = os.path.abspath(os.path.join(os.path.dirname(__file__),'movie.sqlite'))

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    return connection, connection.cursor()

@app.route('/api/movies', methods=['GET'])
def get_movies():
    
    # Get query parameters for filtering and sorting
    director_name = request.args.get('director_name')
    movie_title = request.args.get('movie_title')
    sort_by = request.args.get('sort_by')
    
    # Define the base query
    query = '''SELECT m.title, d.name AS director_name
               FROM movies m
               JOIN directors d ON m.director_id = d.id'''

    # Apply filters
    if director_name:
        query += f" WHERE d.name LIKE '%{director_name}%'"
    if movie_title:
        if director_name:
            query += " AND"
        else:
            query += " WHERE"
        query += f" m.original_title LIKE '%{movie_title}%'"

    # Apply sorting
    if sort_by:
        query += f" ORDER BY {sort_by}"

    # Limit the number of results to 10
    query += ';'

    # Send the query to the execute_query function
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/directors', methods=['GET'])
def get_directors():
    # Get query parameters for  sorting
    sort_by = request.args.get('sort_by')
    # Define the appropriate query
    query = 'SELECT name FROM directors'

    if sort_by:
        query += f" ORDER BY {sort_by}"
    
    query+=';'
    
    # Send the query to the execute_query function
    result = execute_query(query)
    # json_data = json.dumps(result, indent=4)
    return jsonify(result)

def execute_query(query):
    # Establish a new database connection and cursor for each request
    connection, cursor = get_db_connection()

    try:
        # Execute the query
        cursor.execute(query)

        if query.lower().startswith('select'):
            # Fetch the query results as a list of dictionaries
            columns = [column[0] for column in cursor.description]
            # Jsonify the result
            query_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return query_results
    finally:
        # Close the cursor and connection in a 'finally' block to ensure it's always closed
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
