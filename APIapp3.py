# Python libraries
import json, sqlite3
# Site-packages
from flask import Flask, jsonify, request

# Define the application as an instance of Flask
app=Flask(__name__)

# Define the sqlite database file
DATABASE = 'movie.sqlite'



@app.route('/api/movies', methods=['GET'])
def get_movies():
    print(1111111111111111111111)
    # Get query parameters for filtering and sorting
    director_name = request.args.get('director_name')
    film_title = request.args.get('movie_title')
    sort_by = request.args.get('sort_by')

    print(director_name)
    print(film_title)
    
    # Define the base query
    query = '''SELECT m.*, d.name AS director_name
               FROM movies m
               JOIN directors d ON m.director_id = d.id'''

    # Apply filters
    if director_name:
        query += f" WHERE d.name LIKE '%{director_name}%'"
    if film_title:
        if director_name:
            query += " AND"
        else:
            query += " WHERE"
        query += f" m.original_title LIKE '%{film_title}%'"

    # Apply sorting
    if sort_by:
        query += f" ORDER BY {sort_by}"

    # Limit the number of results to 10
    query += ' LIMIT 10;'

    # Send the query to the execute_query function
    result = execute_query(query)
    return jsonify(result)

@app.route('/api/directors', methods=['GET'])
def get_directors():
    # Define the appropriate query
    query = 'SELECT name FROM directors'
    # Send the query to the execute_query function
    result = execute_query(query)
    # json_data = json.dumps(result, indent=4)
    return jsonify(result)

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