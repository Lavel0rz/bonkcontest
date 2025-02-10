import pandas as pd
import requests
import csv
import time
import os
from datetime import datetime
from collections import defaultdict

# API Details
API_URL = "https://api.pet.game/"
QUERY_TEMPLATE = """
query MyQuery {
  attacks(where: {attackerId: %d, createdAt_gt: %d}) {
    items {
      attackerId
      won
      winnerId
    }
    totalCount
  }
}
"""

# Get today's date
TODAY = datetime.now().strftime("%Y-%m-%d")
CSV_FILE = f"leaderboard_{TODAY}.csv"

# Load bonks data (list of pets and their teams)
bonks = pd.read_csv("bonks.csv", header=None, names=["ID", "Name", "Team"])
bonks["ID"] = bonks["ID"].astype(int)
PET_IDS = bonks["ID"].tolist()

def fetch_attacks(pet_id, past_24h):
    """Fetch attack data from the API for a specific pet in the last 24 hours."""
    query = QUERY_TEMPLATE % (pet_id, past_24h)
    response = requests.post(API_URL, json={'query': query})
    
    if response.status_code == 200:
        data = response.json()
        return data["data"]["attacks"]["items"]
    else:
        print(f"Error fetching data for pet {pet_id}:", response.text)
        return []

def update_leaderboard(attacks, leaderboard):
    """Update leaderboard based on net points won/lost."""
    for attack in attacks:
        attacker = attack["attackerId"]
        winner = attack["winnerId"]
        points_won = int(attack["won"]) // 10**12  # Convert from wei

        if attacker in PET_IDS:
            if attacker == winner:
                leaderboard[attacker] += points_won  # Attacker won → gain points
            else:
                leaderboard[attacker] -= points_won  # Attacker lost → lose points

    return leaderboard

def save_leaderboard(leaderboard):
    """Save leaderboard to a CSV file with Name and Team info."""
    leaderboard_df = pd.DataFrame(list(leaderboard.items()), columns=["ID", "Net Points"])
    
    # Merge with bonks data (adding Name and Team)
    final_leaderboard = bonks.merge(leaderboard_df, on="ID", how="left").fillna(0)

    # Save with today's date
    final_leaderboard.to_csv(CSV_FILE, index=False)

def main():
    current_time = int(time.time())  # Current Unix timestamp
    past_24h = current_time - 86400  # 24 hours ago

    print("Fetching latest attacks for all tracked pets...")
    leaderboard = defaultdict(int)  # Start fresh each day

    for pet_id in PET_IDS:
        print(f"Fetching attacks for pet {pet_id}...")
        attacks = fetch_attacks(pet_id, past_24h)
        print(f"Processing {len(attacks)} attacks for pet {pet_id}...")  
        leaderboard = update_leaderboard(attacks, leaderboard)  # Sum new results

    save_leaderboard(leaderboard)


if __name__ == "__main__":
    main()

