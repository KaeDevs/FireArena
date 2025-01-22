
import requests

URL = "https://api.jsonbin.io/v3/b/6790d61ee41b4d34e47ccfc4"
response = requests.get(URL)

headers = {
    "Content-Type": "application/json",
    "X-Master-Key": "$2a$10$zCxD0eePhaxSpav1iZtzzO41se.8HoND.wMVD5IYqeQpGX3QqYfai"
}

response = requests.get(URL, headers=headers)
if response.status_code == 200:
    
    current_data = response.json()['record'] 
    print("Current data:", current_data)
else:
    print(f"Error fetching data: {response.status_code}")
    exit()


new_player_data = {
    "user_id": 67993,
    "username": "kavinm",
    "team_name": "team2",
    "player1": "Player 1a",
    "player2": "Player 2b"
}


current_data.append(new_player_data)

print(current_data)

response = requests.put(URL, headers=headers, json= current_data) 
if response.status_code == 200:
    print("Data updated successfully!")
else:
    print(f"Error: {response.status_code}")