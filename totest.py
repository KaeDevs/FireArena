from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://mkavin2005:hqr5SqhrHI3diFn1@fireplay.dkbtt.mongodb.net/?retryWrites=true&w=majority&appName=FirePlay",  ssl=True, tls=True, tlsAllowInvalidCertificates=False)
db = client["FirePlay"]

# Example teams
team1 = {
    "team_id": "team_001",
    "team_name": "Team Alpha",
    "players": ["Player1", "Player2", "Player3", "Player4"],
    "registration_status": "completed"
}

team2 = {
    "team_id": "team_002",
    "team_name": "Team Beta",
    "players": ["Player5", "Player6", "Player7", "Player8"],
    "registration_status": "completed"
}

# Insert teams into the collection
db.teams.insert_one(team1)
db.teams.insert_one(team2)

print("Teams added successfully!")
