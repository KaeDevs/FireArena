
# import requests

# URL = "https://api.jsonbin.io/v3/b/6790d61ee41b4d34e47ccfc4"
# response = requests.get(URL)

# headers = {
#     "Content-Type": "application/json",
#     "X-Master-Key": "$2a$10$zCxD0eePhaxSpav1iZtzzO41se.8HoND.wMVD5IYqeQpGX3QqYfai"
# }

# response = requests.get(URL, headers=headers)
# if response.status_code == 200:
    
#     current_data = response.json()['record'] 
#     print("Current data:", current_data)
# else:
#     print(f"Error fetching data: {response.status_code}")
#     exit()


# new_player_data = {
#     "user_id": 67993,
#     "username": "kavinm",
#     "team_name": "team2",
#     "player1": "Player 1a",
#     "player2": "Player 2b"
# }


# current_data.append(new_player_data)

# print(current_data)

# response = requests.put(URL, headers=headers, json= current_data) 
# if response.status_code == 200:
#     print("Data updated successfully!")
# else:
#     print(f"Error: {response.status_code}")


import json
import random
from datetime import datetime, timedelta
from math import ceil, log2
from flask import request
import requests

URL = "https://api.jsonbin.io/v3/b/6790d61ee41b4d34e47ccfc4"

headers = {
    "Content-Type": "application/json",
    "X-Master-Key": "$2a$10$zCxD0eePhaxSpav1iZtzzO41se.8HoND.wMVD5IYqeQpGX3QqYfai"
}

# Function to get teams data
def get_teams_data():
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        current_data = response.json()['record']
        print("Current data:", current_data)
    else:
        print(f"Error fetching data: {response.status_code}")
        exit()
    return current_data

# Function to analyze teams
def analyze_teams(teams_data):
    team_count = len(teams_data)
    print(f"Total teams: {team_count}")
    for team in teams_data:
        print(f"Team {team['team_name']} has players: {team['player1']}, {team['player2']}, {team['player3']}, {team['player4']}")
        print(f"Payment status: {team['payment']}")

# Function to calculate the number of rounds and initialize the JSON structure
def initialize_rounds(teams_data):
    total_teams = len(teams_data)
    total_rounds = ceil(log2(total_teams))  # Calculate the total rounds needed
    print(f"Total rounds needed: {total_rounds}")

    # Initialize the structure for all rounds
    tournament_structure = {
        f"round_{i+1}": [] for i in range(total_rounds)
    }

    return tournament_structure, total_rounds

# Function to schedule only the first round of matches
def schedule_round_one(teams_data):
    random.shuffle(teams_data)
    current_time = datetime.now()
    round_one_matches = []
    left_out_team = None

    # Handle odd number of teams: leave out one team for a bye
    if len(teams_data) % 2 != 0:
        left_out_team = teams_data.pop()

    match_id = 1
    for i in range(0, len(teams_data), 2):
        if i + 1 < len(teams_data):
            team1 = teams_data[i]
            team2 = teams_data[i + 1]
            match_room_id = f"room_1_{match_id}"
            match_time = current_time + timedelta(hours=match_id * 2)

            match_details = {
                "round": 1,
                "match_id": match_id,
                "team1": team1['team_name'],
                "team2": team2['team_name'],
                "match_room_id": match_room_id,
                "scheduled_time": match_time.strftime('%Y-%m-%d %H:%M:%S'),
                "winner": None  # Placeholder for spectator updates
            }

            round_one_matches.append(match_details)
            match_id += 1

    return round_one_matches, left_out_team

# Function to save tournament structure to a JSON file
def save_tournament_structure(tournament_structure, round_one_matches, left_out_team):
    # Populate round_one with matches and left-out team
    tournament_structure["round_1"] = {
        "matches": round_one_matches,
        "left_out_team": left_out_team['team_name'] if left_out_team else None
    }

    matURL = "https://api.jsonbin.io/v3/b/6790fa0bad19ca34f8f295be"
    matreq = requests.put(matURL, headers=headers, json=tournament_structure)

    with open('tournament_structure.json', 'w') as f:
        json.dump(tournament_structure, f, indent=4)

# Main function to run the program
def main():
    # Fetch teams data
    teams_data = get_teams_data()

    # Analyze teams
    analyze_teams(teams_data)

    # Initialize tournament structure
    tournament_structure, total_rounds = initialize_rounds(teams_data)

    # Schedule round 1 matches
    round_one_matches, left_out_team = schedule_round_one(teams_data)

    # Save tournament structure with round 1 populated
    save_tournament_structure(tournament_structure, round_one_matches, left_out_team)

    print(f"Tournament structure with {total_rounds} rounds created and saved to tournament_structure.json")

if __name__ == "__main__":
    main()
