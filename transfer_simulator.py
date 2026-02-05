def scale_metric(value, from_team, to_team, from_league, to_league):
    if from_team <= 0 or to_league <= 0 or from_league <= 0 or to_team <= 0:
        return value
    team_factor = to_team / from_team
    league_factor = from_league / to_league
    combined = team_factor * league_factor
    return round(value * combined, 2)


def simulate_player_transfer(
    player_name: str,
    df_2025_26,
    metrics: list,
    potential_team: str,
    potential_league: str,
    team_ratings_df,
    league_ratings: dict,
):
    player_row = df_2025_26[df_2025_26["Player"] == player_name]
    if player_row.empty:
        return f"Player {player_name} not found in 2025-26 data."
    player_row = player_row.iloc[0]

    current_team = player_row["Parent Team"]
    current_league = player_row["League"]

    cur_team_rating = (
        team_ratings_df.set_index("contestantName")
        .get("currentRating", {})
        .get(current_team, 50)
    )
    pot_team_rating = (
        team_ratings_df.set_index("contestantName")
        .get("currentRating", {})
        .get(potential_team, 50)
    )
    cur_league_rating = None
    pot_league_rating = None
    for league_name in league_ratings:
        if league_name in current_league:
            cur_league_rating = league_ratings[league_name]
        if league_name in potential_league:
            pot_league_rating = league_ratings[league_name]
    if cur_league_rating is None:
        cur_league_rating = 50
    if pot_league_rating is None:
        pot_league_rating = 50

    scaled_metrics = {}
    for metric in metrics:
        value = player_row.get(metric, None)
        if value is None:
            scaled_metrics[metric] = None
            continue
        scaled = scale_metric(
            value,
            cur_team_rating,
            pot_team_rating,
            cur_league_rating,
            pot_league_rating,
        )
        scaled_metrics[metric] = round(scaled, 2)

    def to_py(val):
        if hasattr(val, "item"):
            return val.item()
        return val

    comparison = {
        "Current Context": {
            "Team": current_team,
            "League": current_league,
            "Team Rating": cur_team_rating,
            "League Rating": cur_league_rating,
            "Metrics": {m: to_py(player_row.get(m, None)) for m in metrics},
        },
        "Potential Context": {
            "Team": potential_team,
            "League": potential_league,
            "Team Rating": pot_team_rating,
            "League Rating": pot_league_rating,
            "Metrics": scaled_metrics,
        },
    }
    return comparison
