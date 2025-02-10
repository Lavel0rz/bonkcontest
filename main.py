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
top_contributors = df.sort_values(by="Net Points", ascending=False).reset_index(drop=True)

st.subheader("Top Contributors Overall")
st.dataframe(top_contributors.head(10), use_container_width=True)

# Team-Specific Contributors
st.subheader("Top Contributors by Team")
selected_team = st.selectbox("Select a Team", df["Team"].unique())
team_contributors = df[df["Team"] == selected_team].sort_values(by="Net Points", ascending=False).reset_index(drop=True)
st.dataframe(team_contributors, use_container_width=True)

