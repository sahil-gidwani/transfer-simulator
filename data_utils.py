import pandas as pd
import re


def load_data(filepath):
    df = pd.read_csv(filepath)
    df.rename(
        columns={"Team": "Parent Team", "Team within selected timeframe": "Team"},
        inplace=True,
    )
    df["Parent Team"] = df["Parent Team"].fillna(df["Team"])
    df["Season"] = df["League"].str.extract(r"(\d{4}-\d{2})")
    return df
