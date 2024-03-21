# The Recommender
![ARCHITECTURE.png](img%2FARCHITECTURE.png)

This project is the starting point for building a recommendation engine for Netflix users. It has a database that can
handle information about different parts of movies and TV shows, like actors, directors, genres, and where they're made.
using Python and some of its tools - SQLAlchemy for working with the database, and FastAPI for making a web API. The
goal is to manage movie and TV show data and start working on a basic recommendation system.

The ETL process was implemented in the project to seed the database, and a user-friendly interface with Streamlit has
been developed for easy interaction with the database by data analysts and test users.

## Table of Contents

- [Initial Delivery Plan](#InitialDeliveryPlan)
- [Prerequisites](#Prerequisites)
- [Usage](#usage)
- [Features](#features)
- [Future Delivery Plan](#contributing)


## Initial Delivery Plan

1. Assumptions
   The team is comfortable with SQL and Python.
   Real-time data processing is not a primary requirement initially.
   The system is intended for internal use by Netflix's team,
   so security and authentication aspects is not addressed in this project stage.
2. Overall Objectives
   Establish a normalized database to store general information about media, actors, and directors.
   Develop Python APIs for efficient data interaction.
   Ensure the system is user-friendly for data analysts and scientists.
3. Implement basic recommendation framework solution.

### RDBMS Selection

The chosen database for this project is PostgreSQL. It is well-suited for handling complex queries and
efficiently managing large datasets, which are critical requirements for data-intensive applications.
Additionally, PostgreSQL offers excellent scalability options, both vertically and horizontally,
making it essential for meeting the evolving data needs of the project.

### Proposed Data Model

The data model for this project is intricately designed to manage and represent media-related data, encompassing a
variety of entities such as media items, actors, directors, genres, and production countries. It's implemented using
SQLAlchemy, a comprehensive ORM (Object-Relational Mapping) toolkit in Python.

The model primarily revolves around the Media entity, with multiple associations to other entities like Actor, Director,
Genre, and Production. These associations are represented through junction tables, enabling many-to-many relationships.

Entities:

- Media
    - Represents media items (movies or shows).
    - Fields include ID, title, type (movie or show), release year, age certification, runtime, number of seasons (if
      applicable), IMDb score, and IMDb votes.
- Actor
    - Represents actors featured in the media.
    - Each actor has an ID and name.
    - Related to Media through the media_actor association.
- Director
    - Represents directors of the media.
    - Each director has an ID and name.
    - Linked to Media via media_director association.
- Genre
    - Represents genres of media.
    - Each genre has an ID and a genre type.
    - Connected to Media through media_genre association.
- Production
    - Represents the country of production.
    - Each country has an ID and a country code.
    - Associated with Media via media_production association.

Associations:

- media_actor association: Links Media and Actor.
- media_director association: Connects Media and Director.
- media_genre association: Associates Media with Genre.
- media_production association: Joins Media and Production.

Entity-Relationship Diagram:
![DE14_ERD.png](img%2FDE14_ERD.png)

## Prerequisites

Ensure you have the following installed:

- Python (version 3.x)
- pip (Python package manager)
- A virtual environment tool like `venv`
- Postgres database

### Setting Up a Virtual Environment

(Optional but recommended) Create and activate a virtual environment to isolate the project dependencies:

```
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate
```

### Installing Dependencies

Install the necessary Python packages using pip:

```
pip install -r requirements.txt
```

### Environment Variables

Create a .env file in the project root directory.
Add the database connection details:

```
DB_URL="your_database_url"
```

### Running the Web Application with Streamlit

To run the Streamlit application:

```
streamlit run app.py
```

The Streamlit application is now available for viewing in the browser,
usually accessible at: http://localhost:8501.

### Running FastAPI Server

To start the FastAPI server:

```
uvicorn web_api:app --reload
```

This command will start a local server, usually accessible at http://localhost:8000.
The --reload flag is optional and enables auto-reloading of the server when code changes.

### Executing the ETL Process

To seed Postgres database with csv file's content from a `data` folder:

```
python etl.py
```

## Usage

### Interacting with the Web API

Use the FastAPI server URL ( http://127.0.0.1:8000/docs) to access the API endpoints.
You will see the automatic interactive API documentation (provided by Swagger UI).
![FASTAPI.JPG](img%2FFASTAPI.JPG)

### Using the Recommendation Engine

The Streamlit application is available for viewing in the browser, usually accessible at: http://localhost:8501.
Navigate to the recommendation section in the Streamlit interface.
Input your preferences or select criteria to receive movie or TV show recommendations.
![genre.JPG](img%2Fgenre.JPG)

### Exploring database

![db.JPG](img%2Fdb.JPG)

### Features

Based on initial data (IMDB votes and score), the project incorporates the Content-Based Filtering technique.
This method recommends media to users based on their preferences for certain actors or directors.
The recommendations are primarily based on the highest-rated IMDB scores and votes.

```
-- Example in SQL terms
SELECT
    media.title,
    media.release_year
FROM media
JOIN media_actor_association
    ON media.id = media_actor_association.media_id
JOIN actors
    ON media_actor_association.actor_id = actors.id
WHERE actors.name = 'Johnny Depp'
ORDER BY media.imdb_score DESC, media.imdb_votes DESC
LIMIT 10;
```

Additionally, the project offers a most useful feature for recommendations according to a specific IMDB score range (
±0.5) and genre type.

```
-- Example in SQL terms
SELECT 
    media.title,
    media.release_year
FROM media
JOIN genre_media_association 
    ON media.id = genre_media_association.media_id
JOIN
    genre ON genre_media_ssociation.genre_id = genre.id
WHERE
    genre.genre_type = 'Drama' 
    AND media.imdb_score >= min_value 
    AND media.imdb_score <= max_value 
ORDER BY
    media.imdb_votes DESC
LIMIT 10;
```

## Future Delivery Plan

For effective recommendations, it's crucial to continuously collect and integrate user feedback and interactions with
the system. This data helps refine and improve the recommendation algorithms over time. Additionally, utilizing user
data alongside other techniques such as matrix factorization can help identify users with similar tastes and recommend
movies that like-minded users have enjoyed.

If we have access to a large dataset, we can leverage deep learning models to capture complex patterns in user
preferences and movie characteristics. These models may include neural networks trained on user ratings, movie features,
and potentially additional data sources such as movie scripts or scene descriptions.

By extending our model to incorporate user data, we can create user profiles based on their viewing history and
demographic information. This allows us to segment users into different groups and provide targeted recommendations
based on the preferences of each segment.