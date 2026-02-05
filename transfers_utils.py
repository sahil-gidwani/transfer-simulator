import pandas as pd
import re


def main_club_name(team_name):
    if not isinstance(team_name, str):
        return ""
    return re.sub(
        r"\s+(U\d+|II|III|IV|B|C)$", "", team_name, flags=re.IGNORECASE
    ).strip()


def get_transfers(df, season1, season2):
    df1 = df[df["Season"] == season1][["Player", "Parent Team"]]
    df2 = df[df["Season"] == season2][["Player", "Parent Team"]]
    merged = pd.merge(df1, df2, on="Player", suffixes=(f"_{season1}", f"_{season2}"))
    mask = merged.apply(
        lambda row: main_club_name(row[f"Parent Team_{season1}"]).lower()
        != main_club_name(row[f"Parent Team_{season2}"]).lower(),
        axis=1,
    )
    transferred_players = merged[mask]["Player"].unique()
    filtered = df[
        df["Player"].isin(transferred_players) & df["Season"].isin([season1, season2])
    ]
    filtered = filtered.sort_values("Minutes played", ascending=False)
    filtered = filtered.groupby(["Player", "Season"], as_index=False).first()
    counts = filtered["Player"].value_counts()
    valid_players = counts[counts == 2].index
    transfers = filtered[filtered["Player"].isin(valid_players)]
    return transfers
