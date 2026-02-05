import pandas as pd
from mapper import POSITION_GROUPS


def load_data(filepath):
    df = pd.read_csv(filepath)
    df.rename(
        columns={"Team": "Parent Team", "Team within selected timeframe": "Team"},
        inplace=True,
    )
    df["Parent Team"] = df["Parent Team"].fillna(df["Team"])
    df["Season"] = df["League"].str.extract(r"(\d{4}-\d{2})")
    return df


def assign_position_group(main_position):
    for group, positions in POSITION_GROUPS.items():
        if main_position in positions:
            return group
    return "Other"


def add_position_group_column(df):
    df["Position Group"] = df["Main Position"].apply(assign_position_group)
    return df
