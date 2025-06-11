import streamlit as st
import pickle
import pandas as pd
import requests
import logging

# Fallback poster
DEFAULT_POSTER = "https://via.placeholder.com/300x450?text=No+Image"

# Configure logging
logging.basicConfig(level=logging.WARNING)

# Cached poster fetcher
@st.cache_data(show_spinner=False)
def fetch_poster_by_title(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey=bd18ec2c"
        data = requests.get(url).json()
        if data.get('Poster') and data['Poster'] != "N/A":
            return data['Poster']
        else:
            logging.warning(f"No poster found for {title}")
            return DEFAULT_POSTER
    except Exception as e:
        logging.error(f"Error fetching poster for {title}: {e}")
        return DEFAULT_POSTER

# Recommendation logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[movie_index])),
        reverse=True, key=lambda x: x[1]
    )[1:11]  # Get top 10

    recommended_movies = []
    recommended_posters = []

    for i in distances:
        title = movies.iloc[i[0]].title
        poster = fetch_poster_by_title(title)

        if "placeholder.com" not in poster:
            recommended_movies.append(title)
            recommended_posters.append(poster)

        if len(recommended_movies) == 5:
            break

    return recommended_movies, recommended_posters



# Load data
movies_list = pickle.load(open('movie_dict2.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity1.pkl', 'rb'))

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'What was your last watched movie?',
    movies['title'].values
)

if st.button('Recommend'):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name)

    if not names:
        st.warning("Couldn't find recommendations for this movie.")
    else:
        cols = st.columns(len(names))
        for idx, col in enumerate(cols):
            with col:
                st.image(posters[idx], caption=names[idx], use_container_width=True)
