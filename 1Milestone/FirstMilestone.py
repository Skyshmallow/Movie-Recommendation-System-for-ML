"""
Data fetcher using TMDB API
gets and saves 6000 movies in csv file with these features -->

'title', 'genres', 'release_year', 'user_rating', 'keywords', 'director', 'description', 'poster_url', 'trailer_url'

"""

import requests
import csv

#You might need to change to your API key from TMDB
API_KEY = '401aa692d6aa27c92e0fc0adedd58769'
BASE_URL = 'https://api.themoviedb.org/3/'
MOVIE_URL = BASE_URL + 'movie/'
SEARCH_URL = BASE_URL + 'discover/movie'

# features we need 
fields = [
    'title', 'genres', 'release_year', 'user_rating',
    'keywords', 'director', 'description', 'poster_url', 'trailer_url'
]

def get_genres(genre_objects):
    return [genre['name'] for genre in genre_objects]

def fetch_movie_details(movie_id):
    details_url = f"{MOVIE_URL}{movie_id}?api_key={API_KEY}&language=en-US"
    credits_url = f"{MOVIE_URL}{movie_id}/credits?api_key={API_KEY}"
    keywords_url = f"{MOVIE_URL}{movie_id}/keywords?api_key={API_KEY}"
    trailers_url = f"{MOVIE_URL}{movie_id}/videos?api_key={API_KEY}"
    
    try:
        # Fetch details
        details_response = requests.get(details_url).json()
        credits_response = requests.get(credits_url).json()
        keywords_response = requests.get(keywords_url).json()
        trailers_response = requests.get(trailers_url).json()

        # Extract required fields
        title = details_response.get('title', '')
        genres = get_genres(details_response.get('genres', []))
        release_year = details_response.get('release_date', '').split('-')[0]
        user_rating = details_response.get('vote_average', 0.0)
        description = details_response.get('overview', '')
        poster_url = f"https://image.tmdb.org/t/p/w500{details_response.get('poster_path', '')}"

        keywords = [keyword['name'] for keyword in keywords_response.get('keywords', [])]

        # Find director
        director = ''
        for crew_member in credits_response.get('crew', []):
            if crew_member.get('job') == 'Director':
                director = crew_member.get('name')
                break

        # Trailer URL
        trailer_url = ''
        for video in trailers_response.get('results', []):
            if video.get('type') == 'Trailer' and video.get('site') == 'YouTube':
                trailer_url = f"https://www.youtube.com/watch?v={video.get('key')}"
                break

        return [
            title, ', '.join(genres), release_year, user_rating,
            ', '.join(keywords), director, description, poster_url, trailer_url
        ]
    except Exception as e:
        print(f"Error fetching details for movie ID {movie_id}: {e}")
        return None

def fetch_movies_data():

    movies_data = []
    page = 1

    while len(movies_data) < 6000:
        try:
            response = requests.get(
                SEARCH_URL, params={
                    'api_key': API_KEY,
                    'language': 'en-US',
                    'sort_by': 'popularity.desc',
                    'page': page
                }
            ).json()

            for movie in response.get('results', []):
                movie_id = movie['id']
                movie_data = fetch_movie_details(movie_id)
                if movie_data:
                    movies_data.append(movie_data)

            page += 1
        except Exception as e:
            print(f"ERROR on {page}, problem --> {e}")

    return movies_data[:6000]

def save_to_csv(data):
    with open('movies_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        writer.writerows(data)

# Main - Runing stuff above
data = fetch_movies_data()
save_to_csv(data)
print("Saved in movies_data.csv")
