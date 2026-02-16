import pandas as pd
import numpy as np
import re


np.random.seed(42)


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


def generate_dummy_dataset():
    """Generate realistic dummy transfer data"""
    n_players = 2000
    positions = ["GK", "DF", "MF", "FW"]
    position_weights = [0.1, 0.3, 0.35, 0.25]
    data = []

    for i in range(n_players):
        player_name = f"Player_{i+1}"
        position = np.random.choice(positions, p=position_weights)
        age = int(np.clip(np.random.normal(26, 4), 18, 40))

        # Age factor affects performance
        if age < 23:
            age_factor = 0.85 + (age - 18) * 0.03
        elif age <= 28:
            age_factor = 1.0
        else:
            age_factor = 1.0 - (age - 28) * 0.02

        minutes_A = np.random.randint(500, 3000)
        minutes_B = np.random.randint(500, 3000)

        # Base goal-scoring rates per 90 by position
        if position == "GK":
            goals_p90_A = 0.0
            goals_p90_B = 0.0
        elif position == "DF":
            base_rate = np.clip(np.random.normal(0.1, 0.05), 0, 0.3)
            goals_p90_A = base_rate * age_factor
            goals_p90_B = goals_p90_A * np.random.uniform(0.7, 0.9)
        elif position == "MF":
            base_rate = np.clip(np.random.normal(0.3, 0.15), 0, 0.8)
            goals_p90_A = base_rate * age_factor
            goals_p90_B = goals_p90_A * np.random.uniform(0.65, 0.85)
        else:  # FW
            base_rate = np.clip(np.random.normal(0.6, 0.2), 0.1, 1.2)
            goals_p90_A = base_rate * age_factor
            goals_p90_B = goals_p90_A * np.random.uniform(0.6, 0.8)

        # Calculate total goals
        goals_A = int((goals_p90_A * minutes_A / 90))
        goals_B = int((goals_p90_B * minutes_B / 90))

        if position != "GK":
            goals_A = max(0, goals_A + np.random.randint(-2, 3))
            goals_B = max(0, goals_B + np.random.randint(-2, 3))

        goals_p90_A = round((goals_A / minutes_A * 90), 2) if minutes_A > 0 else 0
        goals_p90_B = round((goals_B / minutes_B * 90), 2) if minutes_B > 0 else 0

        data.append(
            {
                "Player": player_name,
                "Age": age,
                "Position": position,
                "Minutes_A": minutes_A,
                "Minutes_B": minutes_B,
                "Goals_A": goals_A,
                "Goals_B": goals_B,
                "Goals_p90_A": goals_p90_A,
                "Goals_p90_B": goals_p90_B,
            }
        )

    return pd.DataFrame(data)
