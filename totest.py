
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
import requests

URL = "https://api.jsonbin.io/v3/b/6790d61ee41b4d34e47ccfc4"
matURL = "https://api.jsonbin.io/v3/b/6790fa0bad19ca34f8f295be"

headers = {
    "Content-Type": "application/json",
    "X-Master-Key": "$2a$10$zCxD0eePhaxSpav1iZtzzO41se.8HoND.wMVD5IYqeQpGX3QqYfai"
}

# Function to fetch tournament data
def fetch_tournament_data():
    response = requests.get(matURL, headers=headers)
    if response.status_code == 200:
        return response.json()['record']
    else:
        print(f"Error fetching tournament data: {response.status_code}")
        return None

# Function to fetch teams data
def get_teams_data():
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        return response.json()['record']
    else:
        print(f"Error fetching teams data: {response.status_code}")
        return None

idURL = "https://api.jsonbin.io/v3/b/679255e6e41b4d34e47d86da"

# Function to assign a room card to a match
import requests

# Assign Room Cards to Scheduled Matches
def assign_rc():
    """
    Assign room cards to already-scheduled matches that don't have one.
    """
    # Fetch room card data
    rc_response = requests.get(idURL, headers=headers)
    if rc_response.status_code != 200:
        print("Error fetching room card data.")
        return False

    rc_data = rc_response.json().get("record", {})
    if not rc_data.get("rc"):
        print("No room cards available.")
        return False

    # Fetch match data
    match_response = requests.get(matURL, headers=headers)
    if match_response.status_code != 200:
        print("Error fetching match data.")
        return False

    match_data = match_response.json()

    # Iterate through all rounds and assign room cards
    room_cards = rc_data["rc"]
    for round_key, matches in match_data.items():
        if round_key.startswith("round_"):  # Process only round keys
            for match in matches:
                if "room_card" not in match or match["room_card"] is None:  # Assign if no room card
                    if not room_cards:
                        print("No more room cards available.")
                        break

                    # Pop the next available room card
                    room_card = room_cards.pop(0)
                    match["room_card"] = room_card
                    print(f"Assigned room card {room_card} to match {match['match_id']} in {round_key}.")

    # Update the match data back to the server
    match_update_response = requests.put(matURL, headers=headers, json=match_data)
    if match_update_response.status_code != 200:
        print("Error updating match data.")
        return False

    # Update the room card data back to the server
    rc_update_response = requests.put(idURL, headers=headers, json=rc_data)
    if rc_update_response.status_code != 200:
        print("Error updating room card data.")
        return False

    return True

def schedule_matches(teams, round_number):
    """
    Schedules matches for a given round and assigns room cards if available.
    """
    # Fetch existing matches (if any)
    response = requests.get(matURL, headers=headers)
    if response.status_code != 200:
        print("Error fetching match data.")
        return [], None

    matches_data = response.json()

    # Create a new list for this round if it doesn't already exist
    round_key = f"round_{round_number}"
    if round_key not in matches_data:
        matches_data[round_key] = []

    # Shuffle teams and create match details
    random.shuffle(teams)
    current_time = datetime.now()
    left_out_team = None

    if len(teams) % 2 != 0:
        left_out_team = teams.pop()

    match_id = len(matches_data[round_key]) + 1  # Continue match IDs from the last

    for i in range(0, len(teams), 2):
        match_details = {
            "round": round_number,
            "match_id": match_id,
            "team1": teams[i]['team_name'],
            "team1_id": teams[i]['id'],
            "team2": teams[i + 1]['team_name'],
            "team2_id": teams[i + 1]['id'],
            "match_room_id": f"room_{round_number}_{match_id}",
            "scheduled_time": (current_time + timedelta(hours=match_id * 2)).strftime('%Y-%m-%d %H:%M:%S'),
            "winner": None,
            "room_card": None
        }
        matches_data[round_key].append(match_details)
        match_id += 1

    # Assign room cards to all matches without one
    assign_rc(matches_data[round_key])

    # Update the match data back to the server
    update_response = requests.put(matURL, headers=headers, json=matches_data)
    if update_response.status_code != 200:
        print("Error updating match data.")
        return [], left_out_team

    return matches_data[round_key], left_out_team

# Function to save tournament data
def save_tournament_data(tournament_data):
    response = requests.put(matURL, headers=headers, json=tournament_data)
    if response.status_code == 200:
        print("Tournament data updated successfully!")
    else:
        print(f"Error updating tournament data: {response.status_code}")

# Main function to handle the rounds
def process_tournament():
    # Step 1: Fetch the tournament data
    tournament_data = fetch_tournament_data()
    if not tournament_data:
        return

    # Step 2: Check if round 1 is empty
    if "round_1" not in tournament_data or not isinstance(tournament_data["round_1"], list) or not tournament_data["round_1"]:
        print("Round 1 is empty. Scheduling matches for Round 1...")
        teams_data = get_teams_data()
        if not teams_data:
            return

        round_one_matches, left_out_team = schedule_matches(teams_data, 1)
        tournament_data["round_1"] = round_one_matches
        tournament_data["left_out_team"] = left_out_team['team_name'] if left_out_team else None
        save_tournament_data(tournament_data)
        print("Round 1 matches scheduled.")
        return

    # Step 3: Process next round if all winners in current round are available
    current_round = 1
    while f"round_{current_round}" in tournament_data:
        round_matches = tournament_data[f"round_{current_round}"]

        # Debugging: Print the structure of round_matches
        print(f"Debug: round_{current_round} matches - {round_matches}")
        
        # Validate that round_matches is a list of dictionaries
        if not isinstance(round_matches, list) or not all(isinstance(match, dict) for match in round_matches):
            print(f"Error: round_{current_round} does not contain valid match data.")
            return

        # Check if any match has a null winner
        if any(match.get('winner') is None for match in round_matches):
            print(f"Round {current_round} has incomplete matches. Waiting for results.")
            return

        # Collect winners from the current round
        winners = [
            {"team_name": match['winner']}
            for match in round_matches if match['winner']
        ]
        if tournament_data["left_out_team"]:
            winners.append({"team_name": tournament_data["left_out_team"]})

        # Schedule the next round
        next_round = current_round + 1
        print(f"Scheduling matches for Round {next_round}...")
        next_round_matches, left_out_team = schedule_matches(winners, next_round)
        tournament_data[f"round_{next_round}"] = next_round_matches
        tournament_data["left_out_team"] = left_out_team['team_name'] if left_out_team else None
        save_tournament_data(tournament_data)
        print(f"Round {next_round} matches scheduled.")
        current_round = next_round

# Run the tournament processing
if __name__ == "__main__":
    process_tournament()
