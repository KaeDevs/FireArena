
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
def assign_rc(matches):
    """
    Assign a room card to the first match that doesn't already have one.
    """
    # Fetch the room card data
    response = requests.get(idURL, headers=headers)
    if response.status_code != 200:
        print("Error fetching room card data.")
        return False

    upreq = response.json().get("record", {})
    if not upreq.get("rc"):
        print("No room cards available.")
        return False

    # Pop the first available room card
    ele = upreq["rc"].pop(0)

    # Assign the room card to the first match without one
    for match in matches:
        if "room_card" not in match:  # Only assign if 'room_card' is not already present
            match["room_card"] = ele
            print(f"Assigned room card {ele} to match {match['match_id']}.")
            break

    # Update the room card list back to the server
    update_response = requests.put(idURL, headers=headers, json=upreq)
    if update_response.status_code != 200:
        print("Error updating room card data.")
        return False

    return True

# Function to schedule matches for a round
def schedule_matches(teams, round_number):
    """
    Schedules matches for a given round and assigns room cards if available.
    """
    random.shuffle(teams)
    current_time = datetime.now()
    matches = []
    left_out_team = None

    if len(teams) % 2 != 0:
        left_out_team = teams.pop()

    
    for i in range(0, len(teams), 2):
        match_details = {
            "round": round_number,
            
            "team1": teams[i]['team_name'],
            "team1_id": teams[i]['id'],
            "team2": teams[i + 1]['team_name'],
            "team2_id": teams[i + 1]['id'],
            # "match_room_id": f"room_{round_number}_{match_id}",
            "scheduled_time": (current_time + timedelta(hours=match_id * 2)).strftime('%Y-%m-%d %H:%M:%S'),
            "winner": None,
            "room_card": None
        }
        matches.append(match_details)
        match_id += 1

    # Assign a room card to one match if available
    assign_rc(matches)

    return matches, left_out_team


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
