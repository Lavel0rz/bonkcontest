import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import base64
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
df_previous["Bonk Points Won"] = df_previous.get("Bonk Points Won", 0)

st.title("Bonk Contest Leaderboard")

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        st.error(f"Image not found: {image_path}")
        return None
    with open(image_path, "rb") as img_file:
        base64_string = base64.b64encode(img_file.read()).decode()
    return base64_string

image_path = r"fpbg.jpg"
base64_image = get_base64_image(image_path)

if base64_image:
    background_image = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("data:image/jpeg;base64,{base64_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(background_image, unsafe_allow_html=True)
else:
    st.warning("Background image not found. Please check the file path.")

# Podium for Top 3 Players
top_contributors = df.groupby(["ID", "Name", "Team"]).sum().reset_index()
top_contributors = top_contributors.sort_values(by="Bonk Points Won", ascending=False).reset_index(drop=True)

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
                <p>Points: {int(top_contributors.iloc[1]['Bonk Points Won'])}</p>
                <p>Team: {top_contributors.iloc[1]['Team']}</p>
            </div>
            <div class="podium-item first">
                <h4>🥇 {top_contributors.iloc[0]['Name']}</h4>
                <p>Points: {int(top_contributors.iloc[0]['Bonk Points Won'])}</p>
                <p>Team: {top_contributors.iloc[0]['Team']}</p>
            </div>
            <div class="podium-item third">
                <h4>🥉 {top_contributors.iloc[2]['Name']}</h4>
                <p>Points: {int(top_contributors.iloc[2]['Bonk Points Won'])}</p>
                <p>Team: {top_contributors.iloc[2]['Team']}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Aggregate Global Points for Teams
df_team_agg = df.groupby("Team")["Bonk Points Won"].sum().reset_index()
df_team_agg = df_team_agg.sort_values(by="Bonk Points Won", ascending=False)

# Aggregate yesterday's points for delta calculation
df_team_prev = df_previous.groupby("Team")["Bonk Points Won"].sum().reset_index()

# Merge current and previous team points to calculate daily changes
df_team_agg = df_team_agg.merge(df_team_prev, on="Team", suffixes=("", "_prev"), how="left").fillna(0)
df_team_agg["Delta"] = df_team_agg["Bonk Points Won"] - df_team_agg["Bonk Points Won_prev"]

st.subheader("Global Points by Team")
col1, col2 = st.columns(2)

for index, row in df_team_agg.iterrows():
    if index % 2 == 0:
        col1.metric(label=row["Team"], value=int(row["Bonk Points Won"]), delta=int(row["Delta"]))
    else:
        col2.metric(label=row["Team"], value=int(row["Bonk Points Won"]), delta=int(row["Delta"]))

# Progress Bars for Team Goals
goals = {"$FP x Coinbase wen?": 2000000, "FRENEMIES": 1500000}
images = {"$FP x Coinbase wen?": "wen.png", "FRENEMIES": "panda3.png"}

st.subheader("Team Bonking Victory Goals")
for team, goal in goals.items():
    current_points = df_team_agg[df_team_agg["Team"] == team]["Bonk Points Won"].sum()
    progress = min(current_points / goal, 1.0)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(images[team], width=100)
    with col2:
        st.write(f"### {team}: {current_points:,.0f} / {goal:,.0f} pts")
        st.progress(progress)

# Top Contributors Overall
st.subheader("Top Contributors Overall")
st.markdown(top_contributors.head(10).to_html(index=False), unsafe_allow_html=True)

# Team-Specific Contributors
st.subheader("Top Contributors by Team")
selected_team = st.selectbox("Select a Team", df["Team"].unique())
team_contributors = df[df["Team"] == selected_team].groupby(["ID", "Name", "Team"]).sum().reset_index().sort_values(by="Bonk Points Won", ascending=False).reset_index(drop=True)
st.markdown(team_contributors.to_html(index=False), unsafe_allow_html=True)

