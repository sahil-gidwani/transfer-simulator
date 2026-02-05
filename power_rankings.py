import pandas as pd
import streamlit as st
from mapper import TEAM_NAME_MAPPING

LEAGUE_ID_TO_NAME = {
    "2kwbbcootiqqgmrzs6o5inle5": "England Premier League 2025-26",
    "6by3h89i2eykc341oz7lv1ddd": "Germany Bundesliga 2025-26",
    "1r097lpxe0xn03ihb7wi98kao": "Italy Serie A 2025-26",
    "34pl8szyvrbwcmfkuocjm3r6t": "Spain La Liga 2025-26",
    "dm5ka0os1e3dxcp3vh05kmp33": "France Ligue 1 2025-26",
}


@st.cache_data
def load_and_filter(filepath="power-rankings-teams.csv"):
    df = pd.read_csv(filepath)
    league_ids = list(LEAGUE_ID_TO_NAME.keys())
    filtered_df = df[df["domesticLeagueId"].isin(league_ids)].copy()
    filtered_df["contestantName"] = (
        filtered_df["contestantName"]
        .map(TEAM_NAME_MAPPING)
        .fillna(filtered_df["contestantName"])
    )
    return filtered_df


def get_league_ratings():
    filtered_df = load_and_filter()
    league_avg = (
        filtered_df.groupby("domesticLeagueId")["currentRating"]
        .mean()
        .round(3)
        .to_dict()
    )
    league_avg_named = {LEAGUE_ID_TO_NAME[k]: v for k, v in league_avg.items()}
    return league_avg_named


def get_team_ratings():
    filtered_df = load_and_filter()
    return filtered_df[["contestantName", "currentRating"]]
