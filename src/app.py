import requests
import streamlit as st

from web_api.web_api import explore_database as _explore_database


def configure_page():
    """ Configure the Streamlit page with title and initial sidebar state. """
    st.set_page_config(
        page_title="Data Engineering Capstone", initial_sidebar_state="expanded"
    )

    st.title("The Recommender")
    st.caption("Turing College. Module 1: Introduction to Data Engineering")
    st.caption("Sprint:4 Data Engineering Capstone Project")
    st.caption("by Vytautas Pliadis")
    pass


# Function to define page navigation
def page_navigation():
    """ Define page navigation using the sidebar radio button. """
    pages = ["Genre and target-sore", "Actor", "Director", "Explore DB"]
    selected_page = st.sidebar.radio("RECOMMENDATION BY:", pages)
    return selected_page


def target_sore():
    st.caption("## Genre And Target IMDb Score (±0.5)")
    genres = [
        "drama",
        "animation",
        "music",
        "action",
        "history",
        "comedy",
        "fantasy",
        "family",
        "war",
        "documentation",
        "sport",
        "thriller",
        "scifi",
        "reality",
        "european",
        "western",
        "romance",
        "crime",
        "horror",
    ]

    # Input fields for recommendations
    genre = st.selectbox("Select genre:", options=genres)
    target_score = st.slider("Select imdb score:", min_value=0, max_value=10, value=7)

    if st.button("Get Recommendation"):
        try:
            response = requests.get(
                f"http://localhost:8005/recommendations/genre-target-score?genre_type={genre}&target_imdb_score={target_score}"
            )
            if response.status_code == 200:
                recommendations = response.json()
                if recommendations:
                    st.caption("## Recommendation:")
                    for media in recommendations:
                        st.caption(f"### {media['title']} ({media['release_year']})")
                else:
                    st.write("No recommendations found.")
            else:
                st.error("Failed to fetch recommendations.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


def favorite_actor():
    st.caption("## Movies And Shows By Actor")
    code = """
    -- Recommendation example in SQL terms
    SELECT media.title, media.release_year
        FROM media
        JOIN media_actor_association ON media.id = media_actor_association.media_id
        JOIN actors ON media_actor_association.actor_id = actors.id
        WHERE actors.name = [name]
        ORDER BY media.imdb_score DESC, media.imdb_votes DESC
        LIMIT 10;"""
    st.code(code, language="sql")
    default_value = "Johnny Depp"
    actor_name = st.text_input("Enter actor name:", default_value)

    if st.button("Get Recommendation"):
        try:
            response = requests.get(
                f"http://localhost:8005/recommendations/actor?name={actor_name}"
            )
            if response.status_code == 200:
                recommendations = response.json()
                if recommendations:
                    st.caption("## Recommendation:")
                    for media in recommendations:
                        st.caption(f"### {media['title']} ({media['release_year']})")
                else:
                    st.write("No recommendations found.")
            else:
                st.error("Failed to fetch recommendations.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


def favorite_director():
    st.caption("## Movies And Shows By Director")
    code = """
    -- Recommendation example in SQL terms
    SELECT media.title, media.release_year
        FROM media
        JOIN media_director_association ON media.id = media_director_association.media_id
        JOIN directors ON media_director_association.director_id = directors.id
        WHERE director.name = 'Johnny Depp'
        ORDER BY media.imdb_score DESC, media.imdb_votes DESC
        LIMIT 10;"""
    st.code(code, language="sql")
    default_value = "Christopher Nolan"
    director_name = st.text_input("Enter director name:", default_value)

    if st.button("Get Recommendation"):
        try:
            response = requests.get(
                f"http://localhost:8005/recommendations/director?name={director_name}"
            )
            if response.status_code == 200:
                recommendations = response.json()
                if recommendations:
                    st.caption("## Recommendation:")
                    for media in recommendations:
                        st.caption(f"### {media['title']} ({media['release_year']})")
                else:
                    st.write("No recommendations found.")
            else:
                st.error("Failed to fetch recommendations.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


def explore_db():
    """ Allows users to execute custom SQL queries on the database and display the results. """
    sql_query = st.sidebar.text_input("Write your SQL query:")
    if st.sidebar.button("EXECUTE QUERY", type="primary"):
        result = _explore_database(sql_query)
        st.caption("### QUERY RESULT:")
        if len(result) > 0:
            st.dataframe(result)


# Main function to run the app
def main():
    configure_page()

    selected_page = page_navigation()
    if selected_page == "Genre and target-sore":
        target_sore()
    elif selected_page == "Actor":
        favorite_actor()
    elif selected_page == "Director":
        favorite_director()
    elif selected_page == "Explore DB":
        explore_db()


if __name__ == "__main__":
    main()
