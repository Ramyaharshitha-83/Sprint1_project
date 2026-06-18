import pandas as pd
from pathlib import Path


def load_excel(path: str, header_row: int = 1) -> pd.DataFrame:
    """
    Generic Excel loader.
    """

    try:
        df = pd.read_excel(path, header=header_row)

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        return df

    except Exception as e:
        print(f"Error loading {path}: {e}")
        raise


def load_core_dataset(file_name: str) -> pd.DataFrame:
    """
    Load dataset from data/raw
    """

    path = Path("data/raw") / file_name

    return load_excel(path, header_row=1)


def load_supporting_dataset(file_name: str) -> pd.DataFrame:
    """
    Load dataset from data/supporting
    """

    path = Path("data/supporting") / file_name

    return load_excel(path, header_row=0)


if __name__ == "__main__":

    companies = load_core_dataset("companies.xlsx")

    print(companies.head())
    print(companies.shape)