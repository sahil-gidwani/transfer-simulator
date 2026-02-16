import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_utils import load_data, add_position_group_column
from utils.power_rankings import get_team_ratings, get_league_ratings
from utils.transfer_simulator import simulate_player_transfer

st.set_page_config(page_title="Rule-Based Transfer Simulation", layout="wide")

st.title("Rule-Based Transfer Simulation")
st.caption(
    """
    This approach simulates player transfers using rule-based scaling factors derived 
    from team competitive ratings and league difficulty metrics.
    """
)
st.divider()


@st.cache_data
def load_cached_data():
    df = load_data("data/filtered_leagues.csv")
    df = add_position_group_column(df)
    return df


@st.cache_data
def load_team_ratings():
    return get_team_ratings()


@st.cache_data
def load_league_ratings():
    return get_league_ratings()


# Load data
df = load_cached_data()
team_ratings_df = load_team_ratings()
league_ratings = load_league_ratings()

# Data Overview
st.header("1. Data Sources")
st.markdown(
    """
    This simulation uses three primary data sources to model transfer performance:
    
    - **Player Statistics:** Historical performance metrics from current season
    - **Team Ratings:** Competitive strength ratings for clubs across leagues
    - **League Ratings:** Relative difficulty and quality rankings of different leagues
    """
)

with st.expander("View Player Data Sample"):
    st.dataframe(df.head(20), use_container_width=True)

with st.expander("View Team Ratings Data"):
    st.dataframe(team_ratings_df, use_container_width=True)

with st.expander("View League Ratings Data"):
    league_df = pd.DataFrame(list(league_ratings.items()), columns=["League", "Rating"])
    st.dataframe(league_df, use_container_width=True)

st.markdown("---")

# Simulation Configuration
st.header("2. Transfer Simulation Configuration")
st.markdown(
    """
    Configure the transfer scenario by selecting a player, potential destination team,
    and the metrics you want to simulate. The model will apply scaling factors based on
    the competitive differences between leagues and teams.
    """
)

filtered_df = df[df["Season"] == "2025-26"].copy()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Player Selection")
    player_name = st.selectbox(
        "Select Player",
        options=sorted(filtered_df["Player"].unique()),
        help="Choose the player whose transfer you want to simulate",
    )

    # Display current player info
    player_info = filtered_df[filtered_df["Player"] == player_name].iloc[0]
    st.info(
        f"""
        **Current Team:** {player_info['Parent Team']}  
        **Current League:** {player_info['League']}  
        **Position:** {player_info['Position']}  
        **Age:** {player_info['Age']}
        """
    )

with col2:
    st.subheader("Destination Selection")
    potential_team = st.selectbox(
        "Select Potential Team",
        options=sorted(team_ratings_df["contestantName"].unique()),
        help="Choose the destination team for the transfer",
    )

    # Find corresponding league
    potential_league_match = filtered_df[filtered_df["Parent Team"] == potential_team]
    if not potential_league_match.empty:
        potential_league = potential_league_match["League"].iloc[0]
        st.info(f"**Destination League:** {potential_league}")
    else:
        potential_league = None
        st.warning("League information not available for selected team")

st.subheader("Simulation Parameters")

col1, col2 = st.columns(2)

with col1:
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
        help="Choose which performance metrics to predict after the transfer",
    )

with col2:
    apply_position_group_scaling = st.checkbox(
        "Apply Position-Specific Scaling",
        value=False,
        help="Apply additional scaling factors based on player position group",
    )

st.markdown("---")

# Run Simulation
st.header("3. Simulation Results")

if st.button("Run Transfer Simulation", type="primary"):
    if not metrics:
        st.error("Please select at least one metric to simulate")
    elif potential_league is None:
        st.error("Could not determine destination league. Please select a valid team.")
    else:
        with st.spinner("Running simulation..."):
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

        if isinstance(simulation_result, str):
            st.error(simulation_result)
        else:
            st.success("Simulation completed successfully!")

            # Extract data
            current_context = simulation_result.get("Current Context", {})
            potential_context = simulation_result.get("Potential Context", {})
            position_averages = simulation_result.get("Position Group Averages", {})

            # Display scenario overview
            st.subheader("Transfer Scenario Overview")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Current Situation**")
                st.metric("Team", current_context.get("Team", "N/A"))
                st.metric("League", current_context.get("League", "N/A"))
                st.metric("Team Rating", f"{current_context.get('Team Rating', 0):.1f}")
                st.metric(
                    "League Rating", f"{current_context.get('League Rating', 0):.1f}"
                )

            with col2:
                st.markdown("**Potential Destination**")
                st.metric("Team", potential_context.get("Team", "N/A"))
                st.metric("League", potential_context.get("League", "N/A"))
                st.metric(
                    "Team Rating", f"{potential_context.get('Team Rating', 0):.1f}"
                )
                st.metric(
                    "League Rating", f"{potential_context.get('League Rating', 0):.1f}"
                )

            st.markdown("---")

            # Performance metrics comparison
            st.subheader("Performance Metrics Comparison")
            st.markdown(
                """
                The table below compares current performance metrics with predicted performance 
                at the destination team, accounting for competitive differences.
                """
            )

            current_metrics = current_context.get("Metrics", {})
            potential_metrics = potential_context.get("Metrics", {})

            # Create comparison dataframe
            comparison_data = []
            for metric in metrics:
                current_val = current_metrics.get(metric)
                potential_val = potential_metrics.get(metric)

                if current_val is not None and potential_val is not None:
                    change = potential_val - current_val
                    change_pct = (change / current_val * 100) if current_val != 0 else 0

                    comparison_data.append(
                        {
                            "Metric": metric,
                            "Current": f"{current_val:.2f}",
                            "Predicted": f"{potential_val:.2f}",
                            "Change": f"{change:+.2f}",
                            "Change %": f"{change_pct:+.1f}%",
                        }
                    )

            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

            # Visualization
            st.subheader("Visual Comparison")

            if len(comparison_data) > 0:
                fig = go.Figure()

                metrics_list = [item["Metric"] for item in comparison_data]
                current_values = [float(item["Current"]) for item in comparison_data]
                predicted_values = [
                    float(item["Predicted"]) for item in comparison_data
                ]

                fig.add_trace(
                    go.Bar(
                        name="Current Performance",
                        x=metrics_list,
                        y=current_values,
                        marker_color="lightblue",
                    )
                )

                fig.add_trace(
                    go.Bar(
                        name="Predicted Performance",
                        x=metrics_list,
                        y=predicted_values,
                        marker_color="lightcoral",
                    )
                )

                fig.update_layout(
                    title="Current vs Predicted Performance Metrics",
                    xaxis_title="Metrics",
                    yaxis_title="Value",
                    barmode="group",
                    height=400,
                )

                st.plotly_chart(fig, use_container_width=True)

            # Position-specific scaling details
            if apply_position_group_scaling and position_averages:
                st.subheader("Position Group Scaling Details")
                st.markdown(
                    """
                    These averages show how players in the same position group perform 
                    at each team and league, used to apply position-specific adjustments.
                    """
                )

                position_data = []
                for metric, averages in position_averages.items():
                    if all(v is not None for v in averages.values()):
                        position_data.append(
                            {
                                "Metric": metric,
                                "Current Team Avg": f"{averages['from_team_pos_avg']:.2f}",
                                "Destination Team Avg": f"{averages['to_team_pos_avg']:.2f}",
                                "Current League Avg": f"{averages['from_league_pos_avg']:.2f}",
                                "Destination League Avg": f"{averages['to_league_pos_avg']:.2f}",
                            }
                        )

                if position_data:
                    position_df = pd.DataFrame(position_data)
                    st.dataframe(position_df, use_container_width=True, hide_index=True)
                else:
                    st.info(
                        "Position group averages not available for selected metrics"
                    )

else:
    st.info(
        "Configure the simulation parameters above and click 'Run Transfer Simulation' to see results"
    )
