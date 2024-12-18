import os
import pandas as pd
import import_ipynb
import random
from flask import Flask, request, jsonify, send_from_directory, session, redirect, render_template
from flask_cors import CORS
import json
import hashlib
from dotenv import load_dotenv

#load environment variables
load_dotenv()

app = Flask(__name__, static_folder=".")
CORS(app, supports_credentials=True)  
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key_change_in_production')

#----------------------------------------
# Deploy (User Management, Recommendations)
#----------------------------------------
#load data
cleaned_data = pd.read_csv('cleaned_movies.csv')
movies_data = pd.read_csv('2Milestone/adultAdded.csv')

#load user data from a json file
def load_users():
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump({}, f)
    with open('users.json', 'r') as f:
        return json.load(f)

# Save user data back to the json file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# register a new user
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

#log in an existing user
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

#log out the current user
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

#Get recommendations based on user-selected movies
@app.route('/')
def deploy_index():
    return render_template('index.html')

@app.route('/index.html')
def serve_index():
    return render_template('index.html')


@app.route('/<path:path>')
def serve_static_file(path):
#if files are in static folder
    return send_from_directory(app.static_folder, path)

from forth import recommend_movies  

@app.route('/recommend', methods=['POST'])
def recommend_endpoint():
    data = request.json
    selected_movies = data.get('selected_movies', [])

    if not selected_movies:
        return jsonify({'error': 'No movies selected'}), 400

#save selected movies for logged-in users
    if 'username' in session:
        username = session['username']
        users = load_users()
        if username in users:
            users[username]['selected_movies'] = selected_movies
            save_users(users)

    #call your recommendation logic
    recommendations = recommend_movies(selected_movies, data_path='cleaned_movies.csv')
    if not recommendations:
        return jsonify({'error': 'No recommendations found'})

    return jsonify({'recommendations': recommendations})

#fetch details for a specific movie
@app.route('/movie-details', methods=['GET'])
def movie_details():
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

#Check if a user is logged in
@app.route('/is_logged_in', methods=['GET'])
def is_logged_in():
    if 'username' in session:
        users = load_users()
        selected_movies = users[session['username']].get('selected_movies', [])
        return jsonify({'logged_in': True, 'username': session['username'], 'selected_movies': selected_movies})
    return jsonify({'logged_in': False})

#Suggest movies based on a search query
@app.route('/suggest', methods=['GET'])
def suggest_movies():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])

# find movies matching the query
    filtered_data = cleaned_data[cleaned_data['title'].str.contains(query, case=False, na=False)].head(10)
    poster_map = movies_data.drop_duplicates(subset='title')[['title', 'poster_url']].set_index('title').to_dict()['poster_url']

#Format suggestions with title and poster URL
    suggestions = filtered_data.apply(
        lambda row: {'title': row['title'], 'poster_url': poster_map.get(row['title'], 'default-poster.jpg')},
        axis=1
    ).tolist()

    return jsonify(suggestions)


#Akinator
try:
    akinator_df = pd.read_csv('deploy/cleaned_adultAdded1.csv')
except Exception as e:
    print(f"Error loading akinator dataset: {e}")
    akinator_df = pd.DataFrame()

class MovieAkinator:
    def __init__(self, dataframe):
        self.possible_movies = dataframe.copy()
        self.asked_elements = set()

#generate the next question based on most frequent genre, keyword, or director
    def generate_question(self):
        if len(self.possible_movies) <= 1:
            return None

#Get the most common genre/keyword/director
        best = self.get_most_frequent_element()
        if not best:
            return None

        q_type, element = best
#create a question
        if q_type == 'genre':
            return {
                "type": "genre",
                "text": f"Is the movie in the {element} genre?",
                "genre": element
            }
        elif q_type == 'keyword':
            return {
                "type": "keyword",
                "text": f"Does the movie involve the keyword '{element}'?",
                "keyword": element
            }
        elif q_type == 'director':
            return {
                "type": "director",
                "text": f"Was the movie directed by {element}?",
                "director": element
            }
        return None

#Find the most common element genre, keyword, director
    def get_most_frequent_element(self):
        genre_counts = {}
        for genres_str in self.possible_movies['genres'].dropna():
            for g in [x.strip() for x in genres_str.split(',') if x.strip()]:
                if ("genre", g) not in self.asked_elements:
                    genre_counts[g] = genre_counts.get(g, 0) + 1

        keyword_counts = {}
        for keywords_str in self.possible_movies['keywords'].dropna():
            for k in [x.strip() for x in keywords_str.split(',') if x.strip()]:
                if ("keyword", k) not in self.asked_elements:
                    keyword_counts[k] = keyword_counts.get(k, 0) + 1

        director_counts = {}
        for d in self.possible_movies['director'].dropna():
            if ("director", d) not in self.asked_elements:
                director_counts[d] = director_counts.get(d, 0) + 1

#combine all elements into a list and sort by count
        all_elements = []
        for g, count in genre_counts.items():
            all_elements.append(("genre", g, count))
        for k, count in keyword_counts.items():
            all_elements.append(("keyword", k, count))
        for d, count in director_counts.items():
            all_elements.append(("director", d, count))

        if not all_elements:
            return None

        all_elements.sort(key=lambda x: x[2], reverse=True)
        return (all_elements[0][0], all_elements[0][1])
    
# Filter movies based on the answer of user to the question
    def filter_movies(self, question, answer):
        if answer is None:
            self.record_asked(question)
            return

        q_type = question['type']
        self.record_asked(question)

        if q_type == 'genre':
            self.possible_movies = self.possible_movies[
                self.possible_movies['genres'].str.contains(rf'\b{question["genre"]}\b', regex=True) == answer
            ]
        
        elif q_type == 'keyword':
            self.possible_movies = self.possible_movies[
                self.possible_movies['keywords'].str.contains(rf'\b{question["keyword"]}\b', regex=True) == answer
            ]
        
        elif q_type == 'director':
            if answer:
                self.possible_movies = self.possible_movies[
                    self.possible_movies['director'] == question['director']
                ]
            else:
                self.possible_movies = self.possible_movies[
                    self.possible_movies['director'] != question['director']
                ]

    def record_asked(self, question):
        if question['type'] == 'genre':
            self.asked_elements.add(("genre", question['genre']))
        elif question['type'] == 'keyword':
            self.asked_elements.add(("keyword", question['keyword']))
        elif question['type'] == 'director':
            self.asked_elements.add(("director", question['director']))

    def get_current_guess(self):
        if len(self.possible_movies) == 1:
            movie = self.possible_movies.iloc[0]
            return {
                "title": movie['title'],
                "year": int(movie['release_year']),
                "poster": movie.get('poster_url', ''),
                "description": movie.get('description', 'No description available')
            }
        return None


akinator_game = None

#Serve the Akinator game page
@app.route('/akinator/')
def akinator_page():
    return render_template('akinator.html')

#start new game
@app.route('/start_game', methods=['POST'])
def start_game():
    global akinator_game
    data = request.json
    include_adult = data.get('include_adult', False)

    filtered_df = akinator_df.copy()
    if not include_adult:
        filtered_df = filtered_df[filtered_df['adult'] == 0]

    akinator_game = MovieAkinator(filtered_df)
    question = akinator_game.generate_question()

    return jsonify({
        "question": question,
        "films_left": len(akinator_game.possible_movies)
    })

# Handle user answers and filter movies
@app.route('/answer', methods=['POST'])
def answer_question():
    global akinator_game
    if akinator_game is None:
        return jsonify({"error": "Game not started. Please start the game first."}), 400

    data = request.json
    question = data.get('question')
    answer = data.get('answer')  # True/False/None

    if not question:
        return jsonify({"error": "Invalid input. Question is required."}), 400


    akinator_game.filter_movies(question, answer)

#check if we have a single guess
    guess = akinator_game.get_current_guess()
    if guess:
        # one movie found, return guess
        return jsonify({"guess": guess})

#check if we have 20 or fewer films left
    if len(akinator_game.possible_movies) <= 20:
        remaining = akinator_game.possible_movies.to_dict('records')
        formatted_movies = []
        for m in remaining:
            formatted_movies.append({
                "title": m['title'],
                "year": int(m['release_year']),
                "poster": m.get('poster_url', ''),
                "description": m.get('description', 'No description available')
            })
        return jsonify({"remaining_movies": formatted_movies})

#else continue asking questions
    next_question = akinator_game.generate_question()
    return jsonify({
        "question": next_question,
        "films_left": len(akinator_game.possible_movies)
    })



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
