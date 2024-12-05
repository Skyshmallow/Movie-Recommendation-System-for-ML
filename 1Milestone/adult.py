import pandas as pd

# Load the dataset
movies_file = 'movies_data.csv'
data = pd.read_csv(movies_file)

# Define a list of adult-related keywords
adult_keywords = [
    "sex", "sexual", "lgbtq", "prostitute", "erotic", "nudity", "nude", "porn", "xxx", "explicit", 
    "sensual", "intimate", "seduction", "fetish", "kinky", "provocative", "raunchy", "sultry", "taboo", "voyeur",
    "bdsm","stripper", "escort", "affair", "orgy", "brothel", 
    "lust", "vulgar", "softcore", "hardcore", "molestation", "incest", "rape", 
    "pedophile", "perversion", "depraved", "lewd", 
    "pornographic", "adult movie", "taboo themes", 
    "indecent", "exposed", "uncensored", "provocation", "seductive", "temptation", 
    "flirtatious", "voyeurism", "depravity", "lecherous", "forbidden", "sensational", 
    "obscenities", "bare", "exposed body", "indulgent"
]
# Function to check for adult content in a text
def check_adult_content(text):
    if pd.isnull(text):
        return 0
    text = text.lower()
    for keyword in adult_keywords:
        if keyword in text:
            return 1
    return 0

# Create the 'adult' feature
# Check both 'description' and 'keywords' columns

data['adult'] = data['description'].apply(check_adult_content) | data['keywords'].apply(check_adult_content)
data['adult'] = data['adult'].astype(int)

# Save the updated dataset
data.to_csv('movies_data_with_adult_feature.csv', index=False)

print("The 'adult' feature has been successfully added and saved to 'movies_data_with_adult_feature.csv'.")