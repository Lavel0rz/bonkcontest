import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Get today's and yesterday's date
TODAY = datetime.now().strftime("%Y-%m-%d")
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# Load all leaderboard files and sum up Net Points
def load_all_leaderboards():
    all_leaderboards = []
    for file in os.listdir():
        if file.startswith("leaderboard_") and file.endswith(".csv"):
            df_temp = pd.read_csv(file)
            all_leaderboards.append(df_temp)
    return pd.concat(all_leaderboards, ignore_index=True) if all_leaderboards else pd.DataFrame()

# Load cumulative leaderboard
df = load_all_leaderboards()

# Load current day's leaderboard
df_today = pd.read_csv(f"leaderboard_{TODAY}.csv") if os.path.exists(f"leaderboard_{TODAY}.csv") else pd.DataFrame()
df_previous = pd.read_csv(f"leaderboard_{YESTERDAY}.csv") if os.path.exists(f"leaderboard_{YESTERDAY}.csv") else df_today.copy()
df_previous["Net Points"] = df_previous.get("Net Points", 0)

st.title("Bonk Contest Leaderboard")

# Podium for Top 3 Players
top_contributors = df.groupby(["ID", "Name", "Team"]).sum().reset_index()
top_contributors = top_contributors.sort_values(by="Net Points", ascending=False).reset_index(drop=True)

if len(top_contributors) >= 3:
    st.markdown(
        """
        <style>
        .podium-container {
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        .podium-item {
            text-align: center;
            padding: 10px;
            border-radius: 10px;
            height: 225px;
            width: 225px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
        }
        .first {
            background-color: #ffd700;
            transform: translateY(-30px);
        }
        .second {
            background-color: #c0c0c0;
        }
        .third {
            background-color: #cd7f32;
            transform: translateY(20px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="podium-container">
            <div class="podium-item second">
                <h4>🥈 {top_contributors.iloc[1]['Name']}</h4>
                <p>Points: {int(top_contributors.iloc[1]['Net Points'])}</p>
                <p>Team: {top_contributors.iloc[1]['Team']}</p>
            </div>
            <div class="podium-item first">
                <h4>🥇 {top_contributors.iloc[0]['Name']}</h4>
                <p>Points: {int(top_contributors.iloc[0]['Net Points'])}</p>
                <p>Team: {top_contributors.iloc[0]['Team']}</p>
            </div>
            <div class="podium-item third">
                <h4>🥉 {top_contributors.iloc[2]['Name']}</h4>
                <p>Points: {int(top_contributors.iloc[2]['Net Points'])}</p>
                <p>Team: {top_contributors.iloc[2]['Team']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Aggregate Global Points for Teams
df_team_agg = df.groupby("Team")["Net Points"].sum().reset_index()
df_team_agg = df_team_agg.sort_values(by="Net Points", ascending=False)

# Aggregate yesterday's points for delta calculation
df_team_prev = df_previous.groupby("Team")["Net Points"].sum().reset_index()

# Merge current and previous team points to calculate daily changes
df_team_agg = df_team_agg.merge(df_team_prev, on="Team", suffixes=("", "_prev"), how="left").fillna(0)
df_team_agg["Delta"] = df_team_agg["Net Points"] - df_team_agg["Net Points_prev"]

st.subheader("Global Points by Team")
col1, col2 = st.columns(2)

for index, row in df_team_agg.iterrows():
    if index % 2 == 0:
        col1.metric(label=row["Team"], value=int(row["Net Points"]), delta=int(row["Delta"]))
    else:
        col2.metric(label=row["Team"], value=int(row["Net Points"]), delta=int(row["Delta"]))

# Top Contributors Overall
st.subheader("Top Contributors Overall")
st.markdown(top_contributors.head(10).to_html(index=False), unsafe_allow_html=True)

# Team-Specific Contributors
# Team-Specific Contributors
st.subheader("Top Contributors by Team")
selected_team = st.selectbox("Select a Team", df["Team"].unique())
team_contributors = df[df["Team"] == selected_team].groupby(["ID", "Name", "Team"]).sum().reset_index().sort_values(by="Net Points", ascending=False).reset_index(drop=True)
st.markdown(team_contributors.to_html(index=False), unsafe_allow_html=True)
