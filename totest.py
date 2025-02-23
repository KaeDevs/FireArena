
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
import logging
import requests
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Assign Room Cards to Already-Scheduled Matches
def assign_rc():
    """
    Assign room cards to already-scheduled matches that don't have one.
    """
    logging.info("Fetching room card data...")
    rc_response = requests.get(idURL, headers=headers)
    if rc_response.status_code != 200:
        logging.error("Error fetching room card data. Status code: %d", rc_response.status_code)
        return False

    rc_data = rc_response.json().get("record", {})
    logging.debug("Room card data fetched: %s", rc_data)

    if not rc_data.get("rc"):
        logging.warning("No room cards available.")
        return False

    logging.info("Fetching match data...")
    match_response = requests.get(matURL, headers=headers)
    if match_response.status_code != 200:
        logging.error("Error fetching match data. Status code: %d", match_response.status_code)
        return False

    match_data = match_response.json()
    logging.debug("Match data fetched: %s", match_data)

    room_cards = rc_data["rc"]
    logging.info("Assigning room cards to matches...")
    for round_key, matches in match_data.items():
        if round_key.startswith("round_"):
            for match in matches:
                if "room_card" not in match or match["room_card"] is None:
                    if not room_cards:
                        logging.warning("No more room cards available.")
                        break

                    room_card = room_cards.pop(0)
                    match["room_card"] = room_card
                    logging.info("Assigned room card %d to match %d in %s.", room_card, match["match_id"], round_key)

    logging.info("Updating match data...")
    match_update_response = requests.put(matURL, headers=headers, json=match_data)
    if match_update_response.status_code != 200:
        logging.error("Error updating match data. Status code: %d", match_update_response.status_code)
        return False

    logging.info("Updating room card data...")
    rc_update_response = requests.put(idURL, headers=headers, json=rc_data)
    if rc_update_response.status_code != 200:
        logging.error("Error updating room card data. Status code: %d", rc_update_response.status_code)
        return False

    logging.info("Room card assignment completed successfully.")
    return True

# Schedule Matches for a Round
def schedule_matches(teams, round_number):
    """
    Schedules matches for a given round and assigns room cards if available.
    """
    logging.info("Fetching existing match data...")
    response = requests.get(matURL, headers=headers)
    if response.status_code != 200:
        logging.error("Error fetching match data. Status code: %d", response.status_code)
        return [], None

    matches_data = response.json()
    logging.debug("Existing match data: %s", matches_data)

    if "rounds" not in matches_data:
        matches_data["rounds"] = []

    logging.info("Shuffling teams and preparing matches...")
    random.shuffle(teams)
    current_time = datetime.now()
    left_out_team = None

    if len(teams) % 2 != 0:
        left_out_team = teams.pop()
        logging.info("Left out team for this round: %s", left_out_team)

    match_id = len(matches_data["rounds"]) + 1

    for i in range(0, len(teams), 2):
        match_details = {
            
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
        matches_data["rounds"].append(match_details)
        logging.debug("Scheduled match: %s", match_details)
        match_id += 1

    logging.info("Assigning room cards to matches in this round...")
    assign_rc()

    logging.info("Updating match data with new schedule...")
    update_response = requests.put(matURL, headers=headers, json=matches_data)
    if update_response.status_code != 200:
        logging.error("Error updating match data. Status code: %d", update_response.status_code)
        return [], left_out_team

    logging.info("Match scheduling completed successfully.")
    return matches_data["rounds"], left_out_team


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

    # Initialize "rounds" list if not present
    if "rounds" not in tournament_data:
        tournament_data["rounds"] = []

    # Step 2: Check if the tournament has any scheduled matches
    if not tournament_data["rounds"]:
        print("No matches found. Scheduling initial matches...")
        teams_data = get_teams_data()
        if not teams_data:
            return

        initial_matches, left_out_team = schedule_matches(teams_data, 1)
        tournament_data["rounds"] = initial_matches
        tournament_data["left_out_team"] = left_out_team['team_name'] if left_out_team else None
        save_tournament_data(tournament_data)
        print("Initial matches scheduled.")
        return

    # Step 3: Process the next round if all winners are available
    print("Processing next round...")

    # Check if any match has a null winner
    if any(match.get('winner') is None for match in tournament_data["rounds"]):
        print("There are incomplete matches. Waiting for results.")
        return

    # Collect winners from the last round
    winners = [
        {"team_name": match['winner']}
        for match in tournament_data["rounds"] if match['winner']
    ]

    if tournament_data.get("left_out_team"):
        winners.append({"team_name": tournament_data["left_out_team"]})

    # Check if there's only one winner left (tournament winner)
    if len(winners) == 1:
        print(f"Tournament Winner: {winners[0]['team_name']}")
        return

    # Schedule next round matches
    print("Scheduling matches for the next round...")
    next_round_number = (len(tournament_data["rounds"]) // 2) + 1
    next_round_matches, left_out_team = schedule_matches(winners, next_round_number)
    tournament_data["rounds"].extend(next_round_matches)
    tournament_data["left_out_team"] = left_out_team['team_name'] if left_out_team else None
    save_tournament_data(tournament_data)
    print(f"Matches for round {next_round_number} scheduled.")

# Run the tournament processing
if __name__ == "__main__":
    process_tournament()
