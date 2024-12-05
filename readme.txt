# Popcorn Picks - Movie Recommendation System

Popcorn Picks is a machine learning project developed by SDU students **Arsen Kenesbayev**, **Nurbek Sagimbayev**, and **Aidos Orynbek** under the guidance of **Yernar Akhmetbet**. This project aims to build a personalized movie recommendation system using data-driven approaches and modern technologies.

## Project Overview
The goal of this project is to provide personalized movie recommendations through the implementation of collaborative and content-based filtering methods. The project includes several stages, from data collection to developing a user-friendly web application.

### Key Features:
- **Data Collection**: Scraped data from various movie sources.
- **Data Preprocessing**: Cleaned and structured data for model training.
- **Exploratory Data Analysis**: Gained insights into the dataset through visualizations.
- **Recommendation Engine**: Developed a machine learning model for personalized recommendations.
- **Interactive Web App**: Built an intuitive interface for users to explore movies and get tailored suggestions.

## Project Requirements and Milestones

### Milestone 1: Data Collection (20 Points)
- **Objective**: Gather movie data (titles, genres, release years, user ratings, etc.) from publicly available sources.
- **Tools & Libraries**: Python, BeautifulSoup, Requests, TMDb API.
- **Deliverables**: Python script for scraping data and a structured CSV file.

### Milestone 2: Data Preprocessing (20 Points)
- **Objective**: Handle missing values, normalize data, encode categorical features, and remove duplicates.
- **Tools & Libraries**: Python, Pandas, NumPy.
- **Deliverables**: Cleaned dataset and a Jupyter Notebook documenting the preprocessing steps.

### Milestone 3: Exploratory Data Analysis (20 Points)
- **Objective**: Analyze and visualize trends in the data, such as genre distribution and user rating patterns.
- **Tools & Libraries**: Pandas, Matplotlib, Seaborn.
- **Deliverables**: Jupyter Notebook with visualizations and summarized insights.

### Milestone 4: Recommendation Model Development (20 Points)
- **Objective**: Train a collaborative or content-based filtering model to recommend movies.
- **Tools & Libraries**: scikit-learn, Pandas.
- **Deliverables**: Implemented model and evaluation results documented in a Jupyter Notebook.

### Milestone 5: Web Application (20 Points)
- **Objective**: Develop an interactive web application for end-users.
- **Tools & Libraries**: HTML, CSS, JavaScript, Flask.
- **Deliverables**: Fully functional web application.

## Technical Implementation

### Data Collection
- Scraped movie data using the TMDb API.
- Extracted essential attributes like genres, keywords, and ratings.

### Preprocessing
- Handled missing values and normalized numerical features.
- Encoded categorical data such as genres and keywords.
- Added features like "adult content" detection using keyword analysis.

### Exploratory Data Analysis
- Visualized genre distributions, user ratings, and keyword trends.
- Identified correlations between genres and user preferences.

### Recommendation Engine
- Implemented content-based filtering using TF-IDF and cosine similarity.
- Integrated genre-based filtering to enhance recommendations.
- Incorporated user ratings into the model for better personalization.

### Web Application
- Built a responsive and user-friendly interface using HTML, CSS, and Bootstrap.
- Integrated the Flask backend to handle API requests for recommendations and suggestions.
- Added functionalities like movie search, preference selection, and trailer previews.

## Usage

### Running the Project Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-repository>/popcorn-picks.git
   ```
2. Navigate to the project directory:
   ```bash
   cd popcorn-picks
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```bash
   python app.py
   ```
5. Open the web application in your browser at `http://localhost:5000`.

## Project Deliverables
- **Code Files**: Scripts and notebooks for each milestone.
- **Cleaned Dataset**: Processed CSV files ready for analysis and modeling.
- **Documentation**: Comprehensive description of the project steps and results.
- **Presentation**: Brief presentation showcasing insights and outcomes.

## Team Members
- **Arsen Kenesbayev**  
  [Instagram Profile](#)  
- **Nurbek Sagimbayev**
- **Aidos Orynbek**

## Mentor
- **Yernar Akhmetbet**

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- **TMDb API** for providing movie data.
- **SDU** for fostering innovation and collaboration.
- **Mentor Yernar Akhmetbet** for guidance and support throughout the project.

---
**Popcorn Picks**  
&copy; 2024 Popcorn Picks. All Rights Reserved.
