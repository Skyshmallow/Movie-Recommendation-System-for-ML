import pandas as pd
import numpy as np

def clean_text(text):
    """
    Clean and standardize text fields
    """
    if pd.isna(text):
        return ''
    return ' '.join(str(text).split())

def clean_genres(genres):
    """
    Clean and standardize genres
    """
    if pd.isna(genres):
        return ''
    # Split, strip, remove duplicates, title case
    genres_list = [g.strip().title() for g in str(genres).split('|')]
    return '|'.join(sorted(set(genres_list)))

def clean_keywords(keywords):
    """
    Clean and standardize keywords
    """
    if pd.isna(keywords):
        return ''
    # Split, strip, lowercase, remove duplicates
    keywords_list = [k.strip().lower() for k in str(keywords).split('|')]
    return '|'.join(sorted(set(keywords_list)))

def preprocess_movie_data(input_file, output_file):
    """
    Comprehensive preprocessing of movie dataset
    """
    # Read the CSV
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    # Columns to clean
    columns_to_clean = [
        'title', 'director', 'description'
    ]

    # Apply text cleaning to specified columns
    for col in columns_to_clean:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)

    # Clean genres and keywords
    if 'genres' in df.columns:
        df['genres'] = df['genres'].apply(clean_genres)
    
    if 'keywords' in df.columns:
        df['keywords'] = df['keywords'].apply(clean_keywords)

    # Ensure adult column is binary
    if 'adult' in df.columns:
        df['adult'] = df['adult'].apply(lambda x: 1 if x == 1 else 0)
    else:
        # Create adult column if not exists
        df['adult'] = 0

    # Handle release year
    if 'release_year' in df.columns:
        # Convert to integer, replace invalid with 0
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce').fillna(0).astype(int)
        
        # Filter out unreasonable years (e.g., before 1800 or future years)
        current_year = pd.Timestamp.now().year
        df = df[(df['release_year'] >= 1800) & (df['release_year'] <= current_year)]

    # Remove rows with no meaningful data
    df = df[
        (df['title'] != '') & 
        (df['genres'] != '') & 
        (df['release_year'] > 0)
    ]

    # Optional: Limit the number of movies to prevent overwhelming the game
    if len(df) > 5000:
        df = df.sample(n=5000, random_state=42)

    # Reset index
    df = df.reset_index(drop=True)

    # Save cleaned CSV
    df.to_csv(output_file, index=False)

    print(f"Preprocessing complete. Processed {len(df)} movies.")
    return df

def main():
    # Example usage
    input_file = 'akinator/adultAdded.csv'  # Your original CSV
    output_file = 'akinator/cleaned_adultAdded.csv'
    
    preprocessed_df = preprocess_movie_data(input_file, output_file)
    
    if preprocessed_df is not None:
        # Display some statistics
        print("\nDataset Statistics:")
        print(f"Total Movies: {len(preprocessed_df)}")
        print("\nSample of Preprocessed Data:")
        print(preprocessed_df.head())

if __name__ == '__main__':
    main()