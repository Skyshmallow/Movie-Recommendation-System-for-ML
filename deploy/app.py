# from flask import Flask, request, jsonify, send_from_directory
# import pandas as pd
# import import_ipynb
# from forth import recommend_movies

# # Load the data
# cleaned_data = pd.read_csv('cleaned_movies.csv')
# movies_data = pd.read_csv('movies.csv')

# app = Flask(__name__, static_folder=".")

# @app.route('/')
# def index():
#     return send_from_directory(app.static_folder, "index.html")

# @app.route('/<path:path>')
# def serve_static_file(path):
#     return send_from_directory(app.static_folder, path)

# @app.route('/recommend', methods=['GET'])
# def recommend_endpoint():
#     titles = request.args.getlist('title')  # Get all titles as a list
#     if not titles:
#         return jsonify({'error': 'No titles provided'})

#     # Call your recommendation logic here
#     recommendations = recommend_movies(titles, data_path='cleaned_movies.csv')

#     if not recommendations:
#         return jsonify({'error': 'Movies not found'})

#     return jsonify({'recommendations': recommendations})



# @app.route('/movie-details', methods=['GET'])
# def movie_details():
#     title = request.args.get('title')
#     movie = movies_data[movies_data['title'] == title]
#     if movie.empty:
#         return jsonify({'error': f"No details found for movie: {title}"})

#     movie = movie.iloc[0]
    
#     # Handle missing trailer_url
#     trailer_url = movie['trailer_url']
#     if pd.isna(trailer_url):
#         trailer_url = None  # Or provide a default value
#     else:
#         trailer_url = trailer_url.replace('watch?v=', 'embed/')

#     return jsonify({
#         'title': movie['title'],
#         'description': movie['description'],
#         'poster_url': movie['poster_url'],
#         'trailer_url': trailer_url  # Embed URL or None
#     })




# @app.route('/suggest', methods=['GET'])
# def suggest_movies():
#     query = request.args.get('query', '').lower()

#     if not query:
#         return jsonify([])

#     # Use cleaned_movies.csv for suggestions
#     suggestions = cleaned_data[cleaned_data['title'].str.lower().str.contains(query, na=False)]['title'].head(10).tolist()
#     return jsonify(suggestions)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)


from flask import Flask, request, jsonify, send_from_directory, session, redirect
import import_ipynb
from forth import recommend_movies
from flask_cors import CORS
import pandas as pd
import os
import hashlib
import json

# Load the data
cleaned_data = pd.read_csv('cleaned_movies.csv')
movies_data = pd.read_csv('movies.csv')

app = Flask(__name__, static_folder=".")
CORS(app, supports_credentials=True)  # Enable CORS with credentials
app.secret_key = 'your_secret_key_here'  # Important for session management

# User management functions
def load_users():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump({}, f)

    with open('users.json', 'r') as f:
        return json.load(f)

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    age = data.get('age')
    gender = data.get('gender')

    if not all([username, password, age, gender]):
        return jsonify({'error': 'All fields are required'}), 400

    users = load_users()

    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = hash_password(password)

    users[username] = {
        'password': hashed_password,
        'age': age,
        'gender': gender
    }

    save_users(users)
    return jsonify({'message': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    users = load_users()

    if username not in users or users[username]['password'] != hash_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['username'] = username
    selected_movies = users[username].get('selected_movies', [])

    return jsonify({'message': 'Login successful', 'selected_movies': selected_movies}), 200


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

# Static file serving routes
@app.route('/')
def index():
    if 'username' not in session:
        return send_from_directory(app.static_folder, "login.html")
    return send_from_directory(app.static_folder, "index.html")

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)

@app.route('/recommend', methods=['POST'])
def recommend_endpoint():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get the logged-in username
    username = session['username']

    # Parse the selected movies from the request
    data = request.json
    selected_movies = data.get('selected_movies', [])

    if not selected_movies:
        return jsonify({'error': 'No movies selected'}), 400

    # Load users and update the selected_movies for the logged-in user
    users = load_users()
    if username in users:
        users[username]['selected_movies'] = selected_movies
        save_users(users)

    # Call your recommendation logic
    recommendations = recommend_movies(selected_movies, data_path='cleaned_movies.csv')

    if not recommendations:
        return jsonify({'error': 'No recommendations found'})

    return jsonify({'recommendations': recommendations})


@app.route('/movie-details', methods=['GET'])
def movie_details():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    title = request.args.get('title')
    movie = movies_data[movies_data['title'] == title]
    if movie.empty:
        return jsonify({'error': f"No details found for movie: {title}"})

    movie = movie.iloc[0]

    trailer_url = movie['trailer_url']
    if pd.isna(trailer_url):
        trailer_url = None
    else:
        trailer_url = trailer_url.replace('watch?v=', 'embed/')

    return jsonify({
        'title': movie['title'],
        'description': movie['description'],
        'poster_url': movie['poster_url'],
        'trailer_url': trailer_url
    })


@app.route('/is_logged_in', methods=['GET'])
def is_logged_in():
    if 'username' in session:
        users = load_users()
        selected_movies = users[session['username']].get('selected_movies', [])
        return jsonify({'logged_in': True, 'username': session['username'], 'selected_movies': selected_movies})
    return jsonify({'logged_in': False})




@app.route('/suggest', methods=['GET'])
def suggest_movies():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])

    suggestions = cleaned_data[cleaned_data['title'].str.lower().str.contains(query, na=False)]['title'].head(10).tolist()
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
