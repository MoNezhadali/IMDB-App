# Python libraries
import os, json, sqlite3
# Site-packages
from flask import Flask, jsonify, request

app = Flask(__name__)

# Exceptions
class UnknownArgumentException(Exception):
    pass

class NoSuchColumnException(Exception):
    pass

# Define the sqlite database file
DATABASE = os.path.abspath(os.path.join(os.path.dirname(__file__),'movie.sqlite'))

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    return connection, connection.cursor()

@app.route('/api/movies', methods=['GET'])
def get_movies():
    allowed_args = ['director_name', 'movie_title', 'sort_by']

    # Check for any unknown arguments
    for arg in request.args.keys():
        if arg not in allowed_args:
            raise UnknownArgumentException(f"Unknown argument '{arg}' provided.")


    # Get query parameters for filtering and sorting
    director_name = request.args.get('director_name')
    movie_title = request.args.get('movie_title')
    sort_by = request.args.get('sort_by')
    
    # Define the base query
    query = '''SELECT m.title
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
        if sort_by=='director_name':
            sort_by='d.name'
        query += f" ORDER BY {sort_by}"
    
    query += ';'
    # Send the query to the execute_query function
    result = execute_API_query(query)
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
    result = execute_API_query(query)
    # json_data = json.dumps(result, indent=4)
    return jsonify(result)

def execute_API_query(query):
    # Establish a new database connection and cursor for each request
    connection, cursor = get_db_connection()

    try:
        # Execute the query
        cursor.execute(query)
        # Fetch the query results as a list of dictionaries
        columns = [column[0] for column in cursor.description]
        # Jsonify the result
        query_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return query_results
    except sqlite3.OperationalError as e:
        if "no such column" in str(e):
            raise NoSuchColumnException("The specified column doesn't exist.")
        raise Exception("Database error occurred.")
    finally:
        # Close the cursor and connection in a 'finally' block to ensure it's always closed
        cursor.close()
        connection.close()


@app.errorhandler(UnknownArgumentException)
def handle_unknown_arg_error(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(NoSuchColumnException)
def handle_no_such_column_error(e):
    return jsonify({"error": str(e)}), 400

@app.errorhandler(Exception)
def handle_generic_error(e):
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
