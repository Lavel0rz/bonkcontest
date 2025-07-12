import streamlit as st
import pandas as pd
import os
from datetime import datetime, timezone, timedelta
import base64

# ─────────────────────────────────────────────────────────────
# Timestamp Handling (Current & Previous Hour)
# ─────────────────────────────────────────────────────────────
NOW = datetime.now()
CURRENT_HOUR = "leaderboard_" + NOW.strftime("%Y-%m-%d_%H00")
PREVIOUS_HOUR = "leaderboard_" + (NOW - timedelta(hours=1)).strftime("%Y-%m-%d_%H00")

# ─────────────────────────────────────────────────────────────
# Load Leaderboard Files
# ─────────────────────────────────────────────────────────────
def load_all_leaderboards():
    all_leaderboards = []
    for file in os.listdir():
        if file.startswith("leaderboard_") and file.endswith(".csv"):
            try:
                df_temp = pd.read_csv(file)
                all_leaderboards.append(df_temp)
            except:
                continue
    return pd.concat(all_leaderboards, ignore_index=True) if all_leaderboards else pd.DataFrame()

# Load hourly leaderboards
df_this_hour = pd.read_csv(f"{CURRENT_HOUR}.csv")
df_prev_hour = pd.read_csv(f"{PREVIOUS_HOUR}.csv")
df_prev_hour["Bonk Points Won"] = df_prev_hour.get("Bonk Points Won", 0)


# Load all files for cumulative stats
df = load_all_leaderboards()

# ─────────────────────────────────────────────────────────────
# Optional: Background Image
# ─────────────────────────────────────────────────────────────
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

image_path = "fpbg.jpg"
base64_image = get_base64_image(image_path)

if base64_image:
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("data:image/jpeg;base64,{base64_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# App Title
# ─────────────────────────────────────────────────────────────

contest_end = datetime(2025, 7, 18, 16, 59, tzinfo=timezone.utc)

placeholder = st.empty()

now = datetime.now(timezone.utc)
remaining = contest_end - now

if remaining.total_seconds() <= 0:
    placeholder.markdown("**Contest has ended!**")
else:
    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    placeholder.markdown(
        f"### Contest ends in: {days}d {hours}h {minutes}m {seconds}s"
    )

    time.sleep(1)
    st.experimental_rerun()
# ─────────────────────────────────────────────────────────────
# Team Delta (Current Hour vs Previous)
# ─────────────────────────────────────────────────────────────
df_team_agg = df_this_hour.groupby("Team")["Bonk Points Won"].sum().reset_index()
df_team_prev = df_prev_hour.groupby("Team")["Bonk Points Won"].sum().reset_index()

df_team_agg = df_team_agg.merge(df_team_prev, on="Team", suffixes=("", "_prev"), how="left").fillna(0)
df_team_agg["Delta"] = df_team_agg["Bonk Points Won"] - df_team_agg["Bonk Points Won_prev"]

st.subheader("📊 Team Points (This Hour vs Last Hour)")
col1, col2 = st.columns(2)
for index, row in df_team_agg.iterrows():
    (col1 if index % 2 == 0 else col2).metric(
        label=row["Team"],
        value=int(row["Bonk Points Won"]),
        delta=int(row["Delta"])
    )

# ─────────────────────────────────────────────────────────────
# Progress Bars for Victory Goals
# ─────────────────────────────────────────────────────────────
goals = {
    "$FP x Coinbase wen?": 2_000_000,
    "FRENEMIES": 1_500_000
}
images = {
    "$FP x Coinbase wen?": "wen.png",
    "FRENEMIES": "panda3.png"
}

st.subheader("🎯 Team Bonking Victory Goals")
for team, goal in goals.items():
    current_points = df[df["Team"] == team]["Bonk Points Won"].sum()
    progress = min(current_points / goal, 1.0)

    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists(images[team]):
            st.image(images[team], width=100)
    with col2:
        st.write(f"### {team}: {current_points:,.0f} / {goal:,.0f} pts")
        st.progress(progress)
st.title("Bonk Contest Leaderboard")


# ─────────────────────────────────────────────────────────────
# Podium (Top 3)
# ─────────────────────────────────────────────────────────────
top_contributors = df.groupby(["ID", "Name", "Team"]).sum().reset_index()
top_contributors = top_contributors.sort_values(by="Bonk Points Won", ascending=False).reset_index(drop=True)

if len(top_contributors) >= 3:
    st.markdown("""
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
    .first { background-color: #ffd700; transform: translateY(-30px); }
    .second { background-color: #c0c0c0; }
    .third { background-color: #cd7f32; transform: translateY(20px); }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
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
    """, unsafe_allow_html=True)



# ─────────────────────────────────────────────────────────────
# Top Contributors Overall
# ─────────────────────────────────────────────────────────────
st.subheader("🏆 Top Contributors Overall (All Time)")
st.markdown(top_contributors.head(10).to_html(index=False), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Team-Specific Top Contributors
# ─────────────────────────────────────────────────────────────
st.subheader("🔍 Top Contributors by Team")
if not df.empty:
    selected_team = st.selectbox("Select a Team", df["Team"].unique())
    team_contributors = df[df["Team"] == selected_team].groupby(["ID", "Name", "Team"]).sum().reset_index()
    team_contributors = team_contributors.sort_values(by="Bonk Points Won", ascending=False)
    st.markdown(team_contributors.to_html(index=False), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Hourly Snapshot Selector
# ─────────────────────────────────────────────────────────────
st.subheader("🕒 View Past Hourly Snapshots")
hourly_files = sorted([f for f in os.listdir() if f.startswith("leaderboard_") and f.endswith(".csv")])
selected_hour_file = st.selectbox("Select Hour", hourly_files[::-1])

if selected_hour_file:
    st.markdown(f"### Snapshot: {selected_hour_file.replace('leaderboard_', '').replace('.csv', '')}")
    df_hourly = pd.read_csv(selected_hour_file)
    hourly_contributors = df_hourly.groupby(["ID", "Name", "Team"]).sum().reset_index()
    hourly_contributors = hourly_contributors.sort_values(by="Bonk Points Won", ascending=False)
    st.markdown(hourly_contributors.to_html(index=False), unsafe_allow_html=True)


