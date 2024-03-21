from data_processing import *
from db_utils import *
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
db_url = os.getenv("DB_URL")

def main():
    try:
        # Create database session
        session = create_database_session(db_url)

        # File paths for data to be merged
        file_path1 = (
            "path-to-file\\raw_credits.csv"
        )
        file_path2 = (
            "path-to-file\\raw_titles.csv"
        )

        media_df = create_df(file_path2)
        # Merge data
        df = merge_dataframe(file_path1, file_path2)

        insert_entities(session, df, "actor")
        insert_entities(session, df, "director")
        insert_genre(session, df)
        insert_production(session, df)
        insert_media(session, media_df)
        insert_media_actors_relations(session, df)
        insert_media_directors_relations(session, df)
        insert_media_genre_relations(session, df)
        insert_media_production_relations(session, df)

        session.commit()
        logger.info("ETL process completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred in the ETL process: {e}")
        raise


if __name__ == "__main__":
    main()
