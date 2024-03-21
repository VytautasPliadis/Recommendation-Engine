import logging

import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_df(path):
    """
    Create a pandas DataFrame from a CSV file and perform data preprocessing.

    Args:
        path (str): The path to the CSV file to read.

    Returns:
        pd.DataFrame: A DataFrame containing the CSV data with preprocessing applied.
    """
    df = pd.read_csv(path)
    df = df.drop(columns=["index"])
    df["imdb_votes"] = df["imdb_votes"].fillna(0)
    df["imdb_score"] = df["imdb_score"].fillna(0)
    # Convert to integer
    df["imdb_votes"] = df["imdb_votes"].astype("Int64")
    return df


def merge_dataframe(file_path1, file_path2):
    """
    Merge two CSV files into a single pandas DataFrame with data preprocessing.

    Args:
        file_path1 (str): The path to the first CSV file.
        file_path2 (str): The path to the second CSV file.

    Returns:
        pd.DataFrame: A merged DataFrame with preprocessing applied.

    Raises:
        Exception: If an error occurs during DataFrame merging.
    """

    try:
        # Load CSV data into pandas DataFrames
        df1 = pd.read_csv(file_path1)
        df2 = pd.read_csv(file_path2)

        # Merge the dataframes
        merged_df = pd.merge(df1, df2, on="id")
        df = merged_df.drop(columns=["index_x", "index_y"])

        df.loc[:, "type"] = df["type"].str.lower()
        df["production_countries"].replace("Lebanon", "LB", regex=True, inplace=True)

        logger.info("DataFrames merged successfully.")
        return df

    except Exception as e:
        logger.error(f"An error occurred during DataFrame merging: {e}")
        raise
