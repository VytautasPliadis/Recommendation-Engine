from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
import streamlit as st

load_dotenv('.env')


def explore_database(sql_query):
    """
    Execute the given SQL query on the database and return the results.

    Parameters:
        sql_query (str): SQL query to be executed.

    Returns:
        list of tuples: Results of the SQL query, returned as a list of tuples.
    """
    if len(sql_query) == 0:
        return []

    # Convert the SQL query string to a textual SQL expression
    sql_query = text(sql_query)

    # Create an engine that represents the core interface to the database
    db_url = os.getenv("DB_URL")
    if not db_url:
        st.error("Database URL is not set.")
        return []

    engine = create_engine(db_url)

    # Create a sessionmaker, which is a factory for creating new Session objects
    Session = sessionmaker(bind=engine)

    results = []
    try:
        # Create a new session
        with Session() as session:
            # Execute the SQL query and fetch results
            results = session.execute(sql_query).fetchall()

    except SQLAlchemyError as e:
        # Handle exceptions
        st.error(f"Database error: {e}")
        return []

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return []

    return results
