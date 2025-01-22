
# https://api.jsonbin.io/v3/b/6790d3f4ad19ca34f8f28613

import requests

URL = "https://api.jsonbin.io/v3/b/6790d61ee41b4d34e47ccfc4"
response = requests.get(URL)

new_data = {
    "user_id": 67890,
    "username": "newuser",
    "team_name": "teamB",
    "player1": "Player Alpha",
    "player2": "Player Beta"
}
headers = {
    "Content-Type": "application/json",
    "X-Master-Key": "$2a$10$zCxD0eePhaxSpav1iZtzzO41se.8HoND.wMVD5IYqeQpGX3QqYfai"
}

# Step 1: Get current data
response = requests.get(URL, headers=headers)
if response.status_code == 200:
    # Get the list directly
    current_data = response.json()['record']  # Accessing the data directly under 'record'
    print("Current data:", current_data)
else:
    print(f"Error fetching data: {response.status_code}")
    exit()

# Step 2: Define new player data to append
new_player_data = {
    "user_id": 67993,
    "username": "kavinm",
    "team_name": "team2",
    "player1": "Player 1a",
    "player2": "Player 2b"
}

# # Step 3: Append new player data
current_data.append(new_player_data)

print(current_data)

# # Step 4: Send the PUT request to update data
response = requests.put(URL, headers=headers, json= current_data) 
if response.status_code == 200:
    print("Data updated successfully!")
else:
    print(f"Error: {response.status_code}")