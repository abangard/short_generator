import streamlit as st
import random


# Main page layout
from constants import TOPIC_MAP
from database import get_opensearch_client
from sm import get_sagemaker_predictor
from util import get_similar_items

predictor = get_sagemaker_predictor()
os_client = get_opensearch_client()

VIDEO_URL = "/Users/abangard/workplace/streamlit/max/resources/clips/"


def main():
    st.title("Max Shorts")

    # Movie selection sidebar
    st.sidebar.header("Filters")
    genre = st.sidebar.selectbox("Topic", TOPIC_MAP.keys())

    st.sidebar.write("**Description**")

    # Display description based on selected genre
    display_description(genre)

    search_query = st.sidebar.text_input("Search", "")
    if st.button("Search", key=f"search_button"):
        display_movies("Search Results", search_query, True)

    # Display movies based on filters
    display_movies(genre, TOPIC_MAP[genre], True)


def display_description(genre):
    st.sidebar.write(TOPIC_MAP[genre])


# Function to display movies
def display_movies(genre, description, similar_button):
    st.subheader(genre)

    # get embeddings for genre description
    inp = {"inputs": description}
    genre_embeddings = predictor.predict(inp)[0][0]

    # get similar movies
    similar_documents = get_similar_items(os_client, genre_embeddings, topk=4)['hits']['hits']

    # get all video ids
    video_urls = []
    video_transcript = []
    video_summary = []
    for document in similar_documents:
        video_urls.append(VIDEO_URL + str(document['_source']['video_id']) + ".mp4")
        video_transcript.append(document['_source']['scene_description'])
        video_summary.append(document['_source']['short_description'])

    # Display videos side by side
    for idx, col in enumerate(st.columns(len(similar_documents))):
        with col:
            st.video(video_urls[idx])
            st.info(video_summary[idx])
            if similar_button:
                if st.button("Similar shorts", key=f"similar_shorts_{idx}"):
                    print("Here")
                    display_movies("More " + genre, video_transcript[idx], False)

    # Set the width of each column
    if similar_button:
        column_width = 1500
    else:
        column_width = 5000
    st.write(
        f'<style>.main .block-container{{max-width: {column_width}px;}}</style>',
        unsafe_allow_html=True,
    )

# Function to play movie trailer
def play_trailer(movie_id):
    pass


if __name__ == "__main__":
    main()
