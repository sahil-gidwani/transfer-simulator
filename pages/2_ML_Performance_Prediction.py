import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error

from utils.transfers_utils import generate_dummy_dataset

st.set_page_config(page_title="ML Performance Prediction", layout="wide")

st.title("Machine Learning Based Performance Prediction")
st.caption(
    """
    This approach uses gradient boosting regression to predict player performance 
    after transferring between leagues based on historical transfer data patterns.
    """
)


@st.cache_data
def load_dummy_data():
    return generate_dummy_dataset()


# Generate dataset
df = load_dummy_data()
df_modeling = df[df["Position"] != "GK"].copy()

st.markdown("---")

# Dataset Overview
st.header("1. Dataset Overview")
st.markdown(
    """
    The dataset contains transfer records for 2,000 players who moved between League A and League B.
    For each player, we track their goal-scoring performance in both leagues, along with age and position.
    """
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Players", len(df))
col2.metric("Defenders", len(df_modeling[df_modeling["Position"] == "DF"]))
col3.metric("Midfielders", len(df_modeling[df_modeling["Position"] == "MF"]))
col4.metric("Forwards", len(df_modeling[df_modeling["Position"] == "FW"]))

st.subheader("Sample Data")
st.dataframe(df_modeling.head(20), use_container_width=True)

# Download button
csv = df_modeling.to_csv(index=False)
st.download_button(
    label="Download Full Dataset (CSV)",
    data=csv,
    file_name="transfer_dataset.csv",
    mime="text/csv",
)

st.markdown("---")

# Exploratory Data Analysis
st.header("2. Exploratory Data Analysis")

tab1, tab2, tab3 = st.tabs(
    ["Performance Distribution", "Age Analysis", "League Comparison"]
)

with tab1:
    st.subheader("Goals per 90 Minutes Distribution")
    st.markdown(
        """
        This shows how goal-scoring rates are distributed across different positions in both leagues.
        Notice how forwards score more frequently than defenders, and performance generally drops in League B.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.histogram(
            df_modeling,
            x="Goals_p90_A",
            color="Position",
            title="League A Performance Distribution",
            labels={"Goals_p90_A": "Goals per 90 Minutes"},
            nbins=30,
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.histogram(
            df_modeling,
            x="Goals_p90_B",
            color="Position",
            title="League B Performance Distribution",
            labels={"Goals_p90_B": "Goals per 90 Minutes"},
            nbins=30,
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Age and Performance Relationship")
    st.markdown(
        """
        Player age significantly impacts performance. Most players peak between 25-28 years old,
        with younger players still developing and older players experiencing gradual decline.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        fig_age_dist = px.histogram(
            df_modeling,
            x="Age",
            title="Age Distribution",
            nbins=22,
            color="Position",
        )
        st.plotly_chart(fig_age_dist, use_container_width=True)

    with col2:
        fig_age_perf = px.scatter(
            df_modeling,
            x="Age",
            y="Goals_p90_A",
            color="Position",
            title="Age vs Performance (League A)",
            labels={"Goals_p90_A": "Goals per 90 Minutes"},
        )
        st.plotly_chart(fig_age_perf, use_container_width=True)

with tab3:
    st.subheader("Cross-League Performance Comparison")
    st.markdown(
        """
        This scatter plot compares player performance between the two leagues. Points below the diagonal line
        indicate players who scored fewer goals in League B, suggesting it is a more competitive league.
        """
    )

    position_stats = (
        df_modeling.groupby("Position")
        .agg({"Goals_p90_A": "mean", "Goals_p90_B": "mean", "Age": "mean"})
        .round(2)
        .reset_index()
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_comparison = px.scatter(
            df_modeling,
            x="Goals_p90_A",
            y="Goals_p90_B",
            color="Position",
            title="League A vs League B Performance",
            labels={
                "Goals_p90_A": "Goals per 90 (League A)",
                "Goals_p90_B": "Goals per 90 (League B)",
            },
            hover_data=["Player", "Age"],
        )

        max_val = max(
            df_modeling["Goals_p90_A"].max(), df_modeling["Goals_p90_B"].max()
        )
        fig_comparison.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode="lines",
                name="Equal performance",
                line=dict(dash="dash", color="gray"),
            )
        )

        st.plotly_chart(fig_comparison, use_container_width=True)

    with col2:
        st.markdown("**Average Performance by Position**")
        st.dataframe(position_stats, use_container_width=True, hide_index=True)

st.markdown("---")

# Model Training
st.header("3. Model Training")
st.markdown(
    """
    We use **Gradient Boosting Regression** to predict player performance in League B. This algorithm
    is well-suited for capturing non-linear relationships such as age curves and position-specific effects.

    **Input Features:**
    - Goals per 90 minutes in League A
    - Player age
    - Position (Defender, Midfielder, Forward)

    **Target Variable:**
    - Goals per 90 minutes in League B
    """
)

# Prepare features
df_modeling["Position_encoded"] = df_modeling["Position"].map(
    {"DF": 0, "MF": 1, "FW": 2}
)

X = df_modeling[["Goals_p90_A", "Age", "Position_encoded"]].values
y = df_modeling["Goals_p90_B"].values

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = GradientBoostingRegressor(
    n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
)
model.fit(X_train, y_train)

# Predictions
y_pred_test = model.predict(X_test)

# Metrics
test_r2 = r2_score(y_test, y_pred_test)
test_mae = mean_absolute_error(y_test, y_pred_test)

st.subheader("Model Performance Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("R-squared Score", f"{test_r2:.3f}")
col2.metric("Mean Absolute Error", f"{test_mae:.3f} goals/90")
col3.metric("Training Samples", f"{len(X_train)}")

st.markdown(
    f"""
    The model achieves an R² score of **{test_r2:.3f}**, meaning it explains {test_r2*100:.1f}% of the variance 
    in League B performance. The mean absolute error of **{test_mae:.3f}** goals per 90 minutes indicates 
    the average prediction error.
    """
)

st.subheader("Prediction Accuracy Visualization")
st.markdown(
    """
    This plot shows actual vs predicted goals per 90 minutes for the test set. Points closer to the
    diagonal line indicate more accurate predictions. The model performs consistently across all positions.
    """
)

test_df = pd.DataFrame(
    {
        "Actual": y_test,
        "Predicted": y_pred_test,
        "Position": X_test[:, 2],
    }
)
test_df["Position"] = test_df["Position"].map({0: "DF", 1: "MF", 2: "FW"})

fig_pred = px.scatter(
    test_df,
    x="Actual",
    y="Predicted",
    color="Position",
    title="Actual vs Predicted Performance (Test Set)",
    labels={"Actual": "Actual Goals per 90", "Predicted": "Predicted Goals per 90"},
)

max_val = max(y_test.max(), y_pred_test.max())
fig_pred.add_trace(
    go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode="lines",
        name="Perfect prediction",
        line=dict(dash="dash", color="gray"),
    )
)

st.plotly_chart(fig_pred, use_container_width=True)

st.markdown("---")

# Interactive Prediction
st.header("4. Interactive Prediction Tool")
st.markdown(
    """
    Use this tool to predict how a player might perform in League B based on their
    current League A statistics, age, and position.
    """
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    input_goals_p90_A = st.number_input("Goals per 90 (League A)", 0.0, 2.0, 0.5, 0.1)

with col2:
    input_age = st.number_input("Player Age", 18, 40, 26)

with col3:
    input_position = st.selectbox("Position", ["DF", "MF", "FW"])

with col4:
    input_minutes_B = st.number_input("Expected Minutes", 500, 3500, 2000, 100)

if st.button("Generate Prediction", type="primary"):
    position_encoded = {"DF": 0, "MF": 1, "FW": 2}[input_position]

    X_input = np.array([[input_goals_p90_A, input_age, position_encoded]])
    predicted_goals_p90_B = model.predict(X_input)[0]
    predicted_goals_p90_B = max(0, predicted_goals_p90_B)

    predicted_total_goals = int((predicted_goals_p90_B * input_minutes_B / 90))

    st.subheader("Prediction Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("League A Performance", f"{input_goals_p90_A:.2f} goals/90")
    with col2:
        st.metric(
            "Predicted League B Performance", f"{predicted_goals_p90_B:.2f} goals/90"
        )
    with col3:
        st.metric("Predicted Total Goals", predicted_total_goals)

    change_pct = (
        ((predicted_goals_p90_B - input_goals_p90_A) / input_goals_p90_A * 100)
        if input_goals_p90_A > 0
        else 0
    )

    if change_pct < -10:
        st.warning(
            f"Expected performance drop of {abs(change_pct):.1f}% - League B appears more competitive"
        )
    elif change_pct > 10:
        st.success(f"Expected performance improvement of {change_pct:.1f}%")
    else:
        st.info(f"Expected similar performance (change: {change_pct:+.1f}%)")
