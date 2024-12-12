import os
import pandas as pd
import random
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Ensure secret key is set
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key_change_in_production')

# Load the movie dataset
try:
    df = pd.read_csv('akinator/cleaned_adultAdded.csv')
except Exception as e:
    print(f"Error loading dataset: {e}")
    df = pd.DataFrame()  # Fallback empty DataFrame

class MovieAkinator:
    def __init__(self, dataframe):
        self.df = dataframe
        self.questions = [
            {"type": "genre", "weight": 0.4, "text": "Is the movie in the {} genre?"},
            {"type": "keyword", "weight": 0.45, "text": "Does the movie involve the keyword '{}'?"},
            {"type": "adult", "weight": 0.05, "text": "Is this an adult-themed movie?"},
            {"type": "director", "weight": 0.05, "text": "Was the movie directed by {}?"},
            {"type": "year_range", "weight": 0.05, "text": "Was the movie released between {} and {} years?"}
        ]
        self.possible_movies = dataframe.copy()
        self.asked_questions = []

    def generate_weighted_question(self):
        if len(self.possible_movies) <= 1:
            return None

        # Select question type based on weighted probability
        question_types = [q['type'] for q in self.questions]
        question_weights = [q['weight'] for q in self.questions]

        question_type = random.choices(question_types, weights=question_weights)[0]

        if question_type == 'genre':
            # Flatten and get unique genres from comma-separated values
            all_genres = set(genre.strip() for genres in self.possible_movies['genres'].dropna().str.split(',') for genre in genres if genre.strip())
            # Filter out already asked genres
            remaining_genres = list(all_genres - set(q[0].get('genre') for q in self.asked_questions if q[0].get('genre')))
            if not remaining_genres:
                return self.generate_weighted_question()  # Retry if no new genres
            genre = random.choice(remaining_genres)
            return {
                "type": "genre",
                "text": self.questions[0]["text"].format(genre),
                "genre": genre
            }

        elif question_type == 'keyword':
            # Flatten and get unique keywords from comma-separated values
            all_keywords = set(keyword.strip() for keywords in self.possible_movies['keywords'].dropna().str.split(',') for keyword in keywords if keyword.strip())
            # Filter out already asked keywords
            remaining_keywords = list(all_keywords - set(q[0].get('keyword') for q in self.asked_questions if q[0].get('keyword')))
            if not remaining_keywords:
                return self.generate_weighted_question()  # Retry if no new keywords
            keyword = random.choice(remaining_keywords)
            return {
                "type": "keyword",
                "text": self.questions[1]["text"].format(keyword),
                "keyword": keyword
            }

        elif question_type == 'adult':
            return {
                "type": "adult",
                "text": self.questions[2]["text"],
                "adult_status": 1
            }

        elif question_type == 'director':
            unique_directors = self.possible_movies['director'].dropna().unique()
            if len(unique_directors) == 0:
                return self.generate_weighted_question()
            director = random.choice(unique_directors)
            return {
                "type": "director",
                "text": self.questions[3]["text"].format(director),
                "director": director
            }

        elif question_type == 'year_range':
            years = self.possible_movies['release_year']
            min_year = years.min()
            max_year = years.max()
            range_start = random.randint(min_year, max_year - 10)
            range_end = range_start + 10
            return {
                "type": "year_range",
                "text": self.questions[4]["text"].format(range_start, range_end),
                "start_year": range_start,
                "end_year": range_end
            }

    def filter_movies(self, question, answer):
        if answer is None:  # "I don't know" case
            return

        if question['type'] == 'genre':
            self.possible_movies = self.possible_movies[
                self.possible_movies['genres'].str.contains(rf'\b{question["genre"]}\b', regex=True) == answer
            ]
        
        elif question['type'] == 'keyword':
            self.possible_movies = self.possible_movies[
                self.possible_movies['keywords'].str.contains(rf'\b{question["keyword"]}\b', regex=True) == answer
            ]
        
        elif question['type'] == 'adult':
            self.possible_movies = self.possible_movies[
                self.possible_movies['adult'] == answer
            ]
        
        elif question['type'] == 'director':
            if answer:
                self.possible_movies = self.possible_movies[
                    self.possible_movies['director'] == question['director']
                ]
            else:
                self.possible_movies = self.possible_movies[
                    self.possible_movies['director'] != question['director']
                ]
        
        elif question['type'] == 'year_range':
            if answer:
                self.possible_movies = self.possible_movies[
                    (self.possible_movies['release_year'] >= question['start_year']) & 
                    (self.possible_movies['release_year'] <= question['end_year'])
                ]
            else:
                self.possible_movies = self.possible_movies[
                    (self.possible_movies['release_year'] < question['start_year']) | 
                    (self.possible_movies['release_year'] > question['end_year'])
                ]

        self.asked_questions.append((question, answer))

    def get_current_guess(self):
        if len(self.possible_movies) == 1:
            movie = self.possible_movies.iloc[0]
            return {
                "title": movie['title'],
                "year": int(movie['release_year']),  # Convert int64 to int
                "poster": movie.get('poster_url', ''),
                "description": movie.get('description', 'No description available')
            }
        return None


# Global game variable
game = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    global game
    game = MovieAkinator(df)
    question = game.generate_weighted_question()
    return jsonify({
        "question": question,
        "films_left": len(game.possible_movies)
    })

@app.route('/answer', methods=['POST'])
def answer_question():
    global game
    if game is None:
        return jsonify({"error": "Game not started. Please start the game first."}), 400

    data = request.json
    question = data.get('question')
    answer = data.get('answer')  # This could be True, False, or None (for "idk")

    if not question:
        return jsonify({"error": "Invalid input. Question is required."}), 400

    # Pass None answer to the game logic without filtering
    if answer is not None:
        game.filter_movies(question, answer)
    else:
        # Add the question to asked questions without filtering if "idk"
        game.asked_questions.append((question, answer))

    guess = game.get_current_guess()
    if guess:
        return jsonify({"guess": guess})

    next_question = game.generate_weighted_question()
    return jsonify({
        "question": next_question,
        "films_left": len(game.possible_movies)
    })

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
