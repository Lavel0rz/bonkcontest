import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Get today's and yesterday's date
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# File paths
current_csv = f"leaderboard_{TODAY}.csv"
previous_csv = f"leaderboard_{YESTERDAY}.csv"

# Load current leaderboard
df = pd.read_csv(current_csv) if os.path.exists(current_csv) else pd.DataFrame()

df_previous = pd.read_csv(previous_csv) if os.path.exists(previous_csv) else df.copy()
df_previous["Net Points"] = df_previous.get("Net Points", 0)  # Default to 0 if missing

st.title("Bonk Contest Leaderboard")
top_contributors = df.sort_values(by="Net Points", ascending=False).reset_index(drop=True)
if len(top_contributors) >= 3:
    podium_cols = st.columns([1, 1, 1])

    # Second Place
    # Second Place
    podium_cols[0].markdown(
        f"""
        <div style="text-align: center; background-color: #c0c0c0; padding: 10px; border-radius: 10px; height: 200px; width: 200px; display: inline-block;">
            <h4>🥈 {top_contributors.iloc[1]['Name']}</h4>
            <p>Points: {int(top_contributors.iloc[1]['Net Points'])}</p>
            <p>Team: {top_contributors.iloc[1]['Team']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # First Place
    podium_cols[1].markdown(
        f"""
        <div style="text-align: center; background-color: #ffd700; padding: 10px; border-radius: 10px; height: 200px; width: 200px; display: inline-block;">
            <h4>🥇 {top_contributors.iloc[0]['Name']}</h4>
            <p>Points: {int(top_contributors.iloc[0]['Net Points'])}</p>
            <p>Team: {top_contributors.iloc[0]['Team']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Third Place
    podium_cols[2].markdown(
        f"""
        <div style="text-align: center; background-color: #cd7f32; padding: 10px; border-radius: 10px; height: 200px; width: 200px; display: inline-block;">
            <h4>🥉 {top_contributors.iloc[2]['Name']}</h4>
            <p>Points: {int(top_contributors.iloc[2]['Net Points'])}</p>
            <p>Team: {top_contributors.iloc[2]['Team']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
# Aggregate Global Points for Teams
team_points = df.groupby("Team")["Net Points"].sum().reset_index()
team_points = team_points.sort_values(by="Net Points", ascending=False)

# Aggregate yesterday's points
team_points_previous = df_previous.groupby("Team")["Net Points"].sum().reset_index()

# Merge current and previous team points
team_points = team_points.merge(team_points_previous, on="Team", suffixes=("", "_prev"), how="left").fillna(0)
team_points["Delta"] = team_points["Net Points"] - team_points["Net Points_prev"]

st.subheader("Global Points by Team")
col1, col2 = st.columns(2)

for index, row in team_points.iterrows():
    if index % 2 == 0:
        col1.metric(label=row["Team"], value=int(row["Net Points"]), delta=int(row["Delta"]))
    else:
        col2.metric(label=row["Team"], value=int(row["Net Points"]), delta=int(row["Delta"]))

# Top Contributors Overall
# Top Contributors Overall
top_contributors = df.sort_values(by="Net Points", ascending=False).reset_index(drop=True).head(10)

st.subheader("Top Contributors Overall")
st.markdown(top_contributors.to_html(index=False), unsafe_allow_html=True)

# Team-Specific Contributors
st.subheader("Top Contributors by Team")
selected_team = st.selectbox("Select a Team", df["Team"].unique())
team_contributors = df[df["Team"] == selected_team].sort_values(by="Net Points", ascending=False).reset_index(drop=True)
st.markdown(team_contributors.to_html(index=False), unsafe_allow_html=True)

