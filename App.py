# Python libraries
import os, sqlite3
# Site-packages
from flask import Flask, render_template, jsonify, request

# Make the app
app = Flask(__name__)

# Define the Exceptions
class UnknownArgumentException(Exception):
    pass

class BadQueryException(Exception):
    pass

class SQLSyntaxException(Exception):
    pass

# Define the sqlite database file
DATABASE = os.path.abspath(os.path.join(os.path.dirname(__file__),'movie.sqlite'))


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    return connection, connection.cursor()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/execute_sql', methods=['POST'])
def execute_sql():
    query = request.form['query']
    result = execute_query(query, output_format='interface')
    return jsonify(result)


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
        if sort_by=='movie_title':
            sort_by='title'
        if sort_by=='director_name':
            sort_by='d.name'
        query += f" ORDER BY {sort_by}"
    query += ';'

    # Send the query to the execute_query function
    result = execute_query(query, output_format='api')
    
    # Send the API call response
    return jsonify({"status": 200, "result": result})



@app.route('/api/directors', methods=['GET'])
def get_directors():
    allowed_args = ['director_name', 'movie_title', 'sort_by']
    # Check for any unknown arguments
    for arg in request.args.keys():
        if arg not in allowed_args:
            raise UnknownArgumentException(f"Unknown argument '{arg}' provided.")
        
    # Get query parameters for  sorting
    sort_by = request.args.get('sort_by')
    director_name = request.args.get('director_name')

    # Define the appropriate query
    query = 'SELECT name FROM directors'
    if director_name:
        query += f" WHERE name LIKE '%{director_name}%'"
    if sort_by:
        if sort_by=='director_name':
            sort_by='name'
        query += f" ORDER BY {sort_by}"
    query+=';'
    
    # Send the query to the execute_query function
    result = execute_query(query, output_format='api')

    # Send the API call response
    return jsonify({"status": 200, "result": result})


def execute_query(query, output_format='api'):
    connection, cursor = get_db_connection()

    try:
        cursor.execute(query)
        
        if query.lower().startswith('select'):
            columns = [desc[0] for desc in cursor.description]
            result = cursor.fetchall()
            
            if output_format == 'api':
                return [dict(zip(columns, row)) for row in result]
            elif output_format == 'interface':
                return {'data': result, 'columns': columns}
        else:
            connection.commit()
            return {'message': 'Query executed successfully.'}
    except sqlite3.OperationalError as e:
        if 'table' in str(e) or 'column' in str(e):
            raise BadQueryException(str(e))
        elif 'syntax' in str(e):
            raise SQLSyntaxException(str(e))
        raise Exception(e)

    finally:
        cursor.close()
        connection.close()


@app.errorhandler(UnknownArgumentException)
def handle_unknown_arg_error(e):
    return jsonify({"status": 400, "error": str(e)}), 400

@app.errorhandler(SQLSyntaxException)
def handle_sql_syntat_error(e):
    return jsonify({"status": 400, "error": f"Your SQL query has syntax error! {str(e)}"}), 400

@app.errorhandler(404)
def handle_404_error(e):
    return jsonify({"status": 404, "error": str(e)}), 404

@app.errorhandler(BadQueryException)
def handle_no_such_column_error(e):
    return jsonify({"status": 404, "error": str(e)}), 404

@app.errorhandler(Exception)
def handle_generic_error(e):
    return jsonify({"status": 500, "error": f"Unexpected Error! {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)