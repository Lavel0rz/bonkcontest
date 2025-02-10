import streamlit as st
import pandas as pd


df = pd.read_csv("leaderboard.csv")


st.title("Bonk Contest Leaderboard")

team_points = df.groupby("Team")["Net Points"].sum().reset_index()
team_points = team_points.sort_values(by="Net Points", ascending=False)

df_previous = df.copy()
df_previous["Net Points"] -= 100  # Simulated change for demonstration
team_points_previous = df_previous.groupby("Team")["Net Points"].sum().reset_index()

team_points = team_points.merge(team_points_previous, on="Team", suffixes=("", "_prev"))
team_points["Delta"] = team_points["Net Points"] - team_points["Net Points_prev"]

st.subheader("Global Points by Team")
col1, col2 = st.columns(2)

for index, row in team_points.iterrows():
    if index % 2 == 0:
        col1.metric(label=row["Team"], value=int(row["Net Points"]), delta=int(row["Delta"]))
    else:
        col2.metric(label=row["Team"], value=int(row["Net Points"]), delta=int(row["Delta"]))


top_contributors = df.sort_values(by="Net Points", ascending=False)

st.subheader("Top Contributors Overall")
st.dataframe(top_contributors.head(10), use_container_width=True)


st.subheader("Top Contributors by Team")
selected_team = st.selectbox("Select a Team", df["Team"].unique())
team_contributors = df[df["Team"] == selected_team].sort_values(by="Net Points", ascending=False)
st.dataframe(team_contributors, use_container_width=True)
