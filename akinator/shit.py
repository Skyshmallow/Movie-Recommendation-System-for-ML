import pandas as pd

# Load Dataset
def load_data():
    # Replace with your dataset path
    return pd.read_csv("akinator/adultAdded.csv")

# Ask Yes/No Questions
def ask_yes_no(question):
    while True:
        answer = input(f"{question} (yes/no): ").strip().lower()
        if answer in ['yes', 'no']:
            return answer == 'yes'
        print("Please answer 'yes' or 'no'.")

# Ask for a Numeric Range
def ask_numeric(question, min_val, max_val):
    while True:
        try:
            answer = int(input(f"{question} (between {min_val} and {max_val}): "))
            if min_val <= answer <= max_val:
                return answer
            print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Please enter a valid number.")

# Game Logic
def akinator_game(data):
    filtered_data = data.copy()

    while len(filtered_data) > 1:
        print(f"\nCurrent number of movies: {len(filtered_data)}")

        # Filter by Genre
        if ask_yes_no("Do you want to filter by genre?"):
            genre = input(f"Choose a genre ({', '.join(filtered_data['genres'].unique())}): ").strip()
            filtered_data = filtered_data[filtered_data['genres'].str.contains(genre, case=False, na=False)]

        # Filter by Release Year
        if ask_yes_no("Do you want to filter by release year?"):
            min_year = ask_numeric("Enter the minimum release year", filtered_data['release_year'].min(), filtered_data['release_year'].max())
            filtered_data = filtered_data[filtered_data['release_year'] >= min_year]

        # Filter by User Rating
        if ask_yes_no("Do you want to filter by user rating?"):
            min_rating = float(input("Enter the minimum rating (0-10): "))
            filtered_data = filtered_data[filtered_data['user_rating'] >= min_rating]

        # Filter by Adult Content
        if ask_yes_no("Should it be adult content?"):
            filtered_data = filtered_data[filtered_data['adult'] == True]
        else:
            filtered_data = filtered_data[filtered_data['adult'] == False]

        if len(filtered_data) == 0:
            print("No movies match your criteria. Try again.")
            return

    # Display the Result
    if len(filtered_data) == 1:
        print("\nWe guessed it!")
        movie = filtered_data.iloc[0]
        print(f"Title: {movie['title']}")
        print(f"Director: {movie['director']}")
        print(f"Description: {movie['description']}")
        print(f"Poster URL: {movie['poster_url']}")
        print(f"Trailer URL: {movie['trailer_url']}")
    else:
        print("\nMultiple movies match your criteria. Try again.")

# Main Function
if __name__ == "__main__":
    data = load_data()
    print("Welcome to Movie Akinator!")
    akinator_game(data)
