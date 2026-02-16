import streamlit as st
from data_utils import load_data, add_position_group_column
from power_rankings import get_team_ratings, get_league_ratings
from transfer_simulator import simulate_player_transfer

st.set_page_config(page_title="Football Transfer Simulator", layout="wide")


def main():
    df = load_data("filtered_leagues.csv")
    df = add_position_group_column(df)
    with st.expander("Raw Data Sample"):
        st.write(df)

    filtered_df = df[df["Season"] == "2025-26"].copy()
    team_ratings_df = get_team_ratings()
    league_ratings = get_league_ratings()
    with st.expander("Team Ratings Data"):
        st.write(team_ratings_df)
    with st.expander("League Ratings Data"):
        st.write(league_ratings)
    st.subheader("Simulating Player Transfer")
    cols = st.columns(2)
    with cols[0]:
        player_name = st.selectbox(
            "Select Player",
            options=filtered_df["Player"].unique(),
        )

    with cols[1]:
        potential_team = st.selectbox(
            "Select Potential Team",
            options=team_ratings_df["contestantName"].unique(),
        )
        # Find its corresponding league
        potential_league = filtered_df[filtered_df["Team"] == potential_team][
            "League"
        ].iloc[0]

    with cols[0]:
        metrics_columns = filtered_df.columns[
            filtered_df.columns.get_loc("Goals") : filtered_df.columns.get_loc(
                "Penalty conversion, %"
            )
            + 1
        ]
        metrics = st.multiselect(
            "Select Metrics to Simulate",
            options=metrics_columns,
            default=["Goals", "Assists"],
        )

    with cols[1]:
        apply_position_group_scaling = st.toggle(
            "Apply Position Group Scaling", value=False
        )

    simulation_result = simulate_player_transfer(
        player_name=player_name,
        df_2025_26=filtered_df,
        metrics=metrics,
        potential_team=potential_team,
        potential_league=potential_league,
        team_ratings_df=team_ratings_df,
        league_ratings=league_ratings,
        apply_position_group_scaling=apply_position_group_scaling,
    )
    st.json(simulation_result)


if __name__ == "__main__":
    main()
