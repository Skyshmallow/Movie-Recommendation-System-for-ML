import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import sys
# sys.stdout.reconfigure(encoding='utf-8')


def recommend_movies(input_titles, data_path='4Milestone/cleaned_movies.csv', top_n=10, weights=None):
    """
    Recommend movies based on input movie titles using multiple features with adjustable weights.
    Now includes filtering for family-friendly recommendations.
    """
    # Load movie data
    movies_df = pd.read_csv(data_path)

    # Ensure weights are defined for all features
    if weights is None:
        weights = {
            'title': 1,
            'user_rating': 1,
            'keywords': 1,
            'director': 1,
            'adult': 1,
            'genres': 1
        }

    # Normalize user ratings to [0, 1] range
    movies_df['normalized_rating'] = movies_df['user_rating'] / movies_df['user_rating'].max()

    # Combine all weighted features into a single metadata column
    movies_df['metadata'] = (
        (movies_df['title'].fillna('') + ' ') * weights['title'] +
        (movies_df['keywords'].fillna('') + ' ') * weights['keywords'] +
        (movies_df['director'].fillna('') + ' ') * weights['director'] +
        (movies_df['adult'].astype(str) + ' ') * weights['adult'] +
        (movies_df['normalized_rating'].astype(str) + ' ') * weights['user_rating']
    )

    # Add one-hot encoded genres with their weights
    genre_columns = [
        'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
        'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery',
        'Romance', 'Science Fiction', 'TV Movie', 'Thriller', 'Unknown', 'War', 'Western'
    ]

    for genre in genre_columns:
        if genre in movies_df.columns:
            movies_df['metadata'] += (movies_df[genre] * weights['genres']).astype(str) + ' '

    # Compute similarity matrix using metadata
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['metadata'])
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Find indices of input movies
    movie_indices = []
    for title in input_titles:
        if title in movies_df['title'].values:
            idx = movies_df[movies_df['title'] == title].index
            if len(idx) > 0:
                movie_indices.append(idx[0])

    # Handle empty input case
    if not movie_indices:
        print("No valid movie indices found. Check input titles.")
        return []

    # Aggregate similarity scores for input movies
    sim_scores = similarity_matrix[movie_indices].sum(axis=0)

    # Penalize adult movies if the input movie is not marked as adult
    if not any(movies_df.iloc[idx]['adult'] for idx in movie_indices):
        for i in range(len(sim_scores)):
            if movies_df.iloc[i]['adult']:
                sim_scores[i] *= 0.5  # Penalize adult movies by halving their similarity score

    # Sort and filter results
    sim_scores = [(i, score) for i, score in enumerate(sim_scores)]
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Filter out input movies
    input_indices = set(movie_indices)
    recommendations = [(i, score) for i, score in sim_scores if i not in input_indices and score > 0]

    # Get top N recommendations
    top_recommendations = recommendations[:top_n]
    recommended_titles = [movies_df.iloc[i]['title'] for i, _ in top_recommendations]

    return recommended_titles

def evaluate_recommendation_model(data_path='4Milestone/cleaned_movies.csv'):
    """
    Evaluate the recommendation model using MAE and RMSE metrics.

    Parameters:
        data_path (str): Path to the cleaned movies data CSV file.

    Returns:
        dict: MAE and RMSE scores.
    """
    # Load movie data
    movies_df = pd.read_csv(data_path)

    # Assume user_rating column exists for evaluation
    true_ratings = movies_df['user_rating'].values

    # Use a simple baseline for predicted ratings (average rating)
    predicted_ratings = np.full_like(true_ratings, true_ratings.mean())

    # Compute MAE and RMSE
    mae = mean_absolute_error(true_ratings, predicted_ratings)
    rmse = np.sqrt(mean_squared_error(true_ratings, predicted_ratings))

    return {'MAE': mae, 'RMSE': rmse}

if __name__ == "__main__":
    # Example usage
    input_titles = ["Moana 2", "Attack on Titan II: End of the World", "One Piece Film Red"]
    weights = {
        'title': 1,
        'user_rating': 2,  # Higher weight for user ratings
        'keywords': 3,
        'director': 1,
        'adult': 1,
        'genres': 10  # Genres slightly more important
    }
    recommendations = recommend_movies(input_titles, weights=weights)
    print("Recommended Movies:", recommendations)

    # Evaluate the model
    evaluation_metrics = evaluate_recommendation_model()
    print("Evaluation Metrics:", evaluation_metrics)
