def scale_metric(
    value,
    from_team_rating,
    to_team_rating,
    from_league_rating,
    to_league_rating,
    from_team_pos_avg=None,
    to_team_pos_avg=None,
    from_league_pos_avg=None,
    to_league_pos_avg=None,
    use_position_scaling=True,
    rating_sensitivity=2.0,
    position_weight=0.4,
):
    """
    Simple power-based scaling - easier to understand and tune

    rating_sensitivity: Controls amplification (1.0 = linear, 2.0 = squared, 3.0 = cubed)
    position_weight: How much position context matters (0.5 = square root, 1.0 = full ratio)
    """

    # Convert ratings to ratios (how much better/worse)
    team_ratio = to_team_rating / from_team_rating if from_team_rating > 0 else 1
    league_ratio = from_league_rating / to_league_rating if to_league_rating > 0 else 1

    # Amplify using power function
    team_effect = team_ratio**rating_sensitivity
    league_effect = league_ratio**rating_sensitivity

    # Base multiplier from ratings only
    base_multiplier = team_effect * league_effect

    # Position context (only if enabled and data available)
    if use_position_scaling:
        context_effect = 1.0

        if from_team_pos_avg and to_team_pos_avg and from_team_pos_avg > 0:
            ratio = to_team_pos_avg / from_team_pos_avg
            context_effect *= ratio**position_weight

        if from_league_pos_avg and to_league_pos_avg and from_league_pos_avg > 0:
            ratio = to_league_pos_avg / from_league_pos_avg
            context_effect *= ratio**position_weight

        # Blend base and context
        final_multiplier = base_multiplier * context_effect
    else:
        # No position scaling - use base only
        final_multiplier = base_multiplier

    # Apply bounds to prevent extreme values
    final_multiplier = max(0.3, min(final_multiplier, 3.0))

    scaled_value = value * final_multiplier
    return round(scaled_value, 2)


def simulate_player_transfer(
    player_name: str,
    df_2025_26,
    metrics: list,
    potential_team: str,
    potential_league: str,
    team_ratings_df,
    league_ratings: dict,
    apply_position_group_scaling: bool = False,
):
    player_row = df_2025_26[df_2025_26["Player"] == player_name]
    if player_row.empty:
        return f"Player {player_name} not found in 2025-26 data."
    player_row = player_row.iloc[0]

    current_team = player_row["Parent Team"]
    current_league = player_row["League"]
    position_group = player_row.get("Position Group", None)

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
    debug_stats = {}
    for metric in metrics:
        value = player_row.get(metric, None)
        if value is None:
            scaled_metrics[metric] = None
            debug_stats[metric] = {
                "from_team_pos_avg": None,
                "to_team_pos_avg": None,
                "from_league_pos_avg": None,
                "to_league_pos_avg": None,
            }
            continue

        from_team_pos_avg = to_team_pos_avg = None
        from_league_pos_avg = to_league_pos_avg = None

        if apply_position_group_scaling and position_group:
            from_team_group = df_2025_26[
                (df_2025_26["Parent Team"] == current_team)
                & (df_2025_26["Position Group"] == position_group)
            ][metric]
            to_team_group = df_2025_26[
                (df_2025_26["Parent Team"] == potential_team)
                & (df_2025_26["Position Group"] == position_group)
            ][metric]
            from_team_pos_avg = from_team_group.mean()
            to_team_pos_avg = to_team_group.mean()

            from_league_group = df_2025_26[
                (df_2025_26["League"] == current_league)
                & (df_2025_26["Position Group"] == position_group)
            ][metric]
            to_league_group = df_2025_26[
                (df_2025_26["League"] == potential_league)
                & (df_2025_26["Position Group"] == position_group)
            ][metric]
            from_league_pos_avg = from_league_group.mean()
            to_league_pos_avg = to_league_group.mean()

        scaled = scale_metric(
            value,
            cur_team_rating,
            pot_team_rating,
            cur_league_rating,
            pot_league_rating,
            from_team_pos_avg,
            to_team_pos_avg,
            from_league_pos_avg,
            to_league_pos_avg,
            use_position_scaling=apply_position_group_scaling,
        )
        scaled_metrics[metric] = round(scaled, 2)
        debug_stats[metric] = {
            "from_team_pos_avg": (
                round(from_team_pos_avg, 2) if from_team_pos_avg is not None else None
            ),
            "to_team_pos_avg": (
                round(to_team_pos_avg, 2) if to_team_pos_avg is not None else None
            ),
            "from_league_pos_avg": (
                round(from_league_pos_avg, 2)
                if from_league_pos_avg is not None
                else None
            ),
            "to_league_pos_avg": (
                round(to_league_pos_avg, 2) if to_league_pos_avg is not None else None
            ),
        }

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
    if apply_position_group_scaling:
        comparison["Position Group Averages"] = debug_stats

    return comparison
