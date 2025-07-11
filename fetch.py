import pandas as pd
import requests
import time
import os
from datetime import datetime
from collections import defaultdict

# API Details
API_URL = "https://api.pet.game/"
QUERY_TEMPLATE = """
query MyQuery {
  attacks(where: {attackerId: %d, winnerId: %d, createdAt_gt: %d}) {
    items {
      attackerId
      won
    }
    totalCount
  }
}
"""

# Get today's date
TODAY = datetime.now().strftime("%Y-%m-%d")
CSV_FILE = f"leaderboard_{datetime.now().strftime('%Y-%m-%d_%H00')}.csv"

# Load bonks data (list of pets and their teams)
bonks = pd.read_csv("bonks.csv", header=None, names=["ID", "Name", "Team"])
bonks["ID"] = bonks["ID"].astype(int)
PET_IDS = bonks["ID"].tolist()

def fetch_attacks(pet_id, past_24h):
    """Fetch attack data from the API for a specific pet in the last 24 hours where attacker is the winner."""
    query = QUERY_TEMPLATE % (pet_id, pet_id, past_24h)
    response = requests.post(API_URL, json={'query': query})
    
    if response.status_code == 200:
        data = response.json()
        return data["data"]["attacks"]["items"]
    else:
        print(f"Error fetching data for pet {pet_id}:", response.text)
        return []

def update_leaderboard(attacks, leaderboard):
    """Update leaderboard based on points won in bonks only."""
    for attack in attacks:
        attacker = attack["attackerId"]
        points_won = int(attack["won"]) // 10**12  # Convert from wei
        
        if attacker in PET_IDS:
            leaderboard[attacker] += points_won  # Sum only points won

    return leaderboard

def save_leaderboard(leaderboard):
    """Save leaderboard to a CSV file with Name and Team info."""
    leaderboard_df = pd.DataFrame(list(leaderboard.items()), columns=["ID", "Bonk Points Won"])
    
    # Merge with bonks data (adding Name and Team)
    final_leaderboard = bonks.merge(leaderboard_df, on="ID", how="left").fillna(0)

    # Save with today's date
    final_leaderboard.to_csv(CSV_FILE, index=False)

def main():
    current_time = int(time.time())  # Current Unix timestamp
    past_1h = current_time - 3600  # 1 hour ago

    print("Fetching latest attacks for all tracked pets in the last hour...")
    leaderboard = defaultdict(int)

    for pet_id in PET_IDS:
        print(f"Fetching attacks for pet {pet_id}...")
        attacks = fetch_attacks(pet_id, past_1h)
        print(f"Processing {len(attacks)} attacks for pet {pet_id}...")  
        leaderboard = update_leaderboard(attacks, leaderboard)

    save_leaderboard(leaderboard)

if __name__ == "__main__":
    main()

