from sqlite3 import Time
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from flask import Flask, request
import totest
import logging
import time
from pymongo import MongoClient, errors
import telegram
import requests


# Flask app
app = Flask(__name__)
creator = False
# Telegram Bot Token
BOT_TOKEN = "7592940575:AAFtJnf4DqUeKtVdfmPx_d4wqbf3lwYOlCM"
URL = "https://api.jsonbin.io/v3/b/6790d61ee41b4d34e47ccfc4"
idURL = "https://api.jsonbin.io/v3/b/679255e6e41b4d34e47d86da"
matURL = "https://api.jsonbin.io/v3/b/6790fa0bad19ca34f8f295be"
creURL = "https://api.jsonbin.io/v3/b/6790e619acd3cb34a8d10fca"
headers = {
    "Content-Type": "application/json",
    "X-Master-Key": "$2a$10$zCxD0eePhaxSpav1iZtzzO41se.8HoND.wMVD5IYqeQpGX3QqYfai"
}
bot = Bot(token=BOT_TOKEN)

cr_name = ""

# Updater and Dispatcher
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


TOURNAMENT_REGISTRATIONS = {
    "username": "kavinm",
    "id":"123temp",
    "match_id": 1,
    "team_name": "team2",
    "player1": "Player 1a",
    "player2": "Player 2b",
    "player3": "Player 2b",
    "player4": "Player 2b",
    "transaction_id": "false",
    "payment": "false",
    "roomid" : None,
    "creator" : False
}  # Dictionary to store registrations

# Conversation steps
TEAM_NAME, PLAYER1, PLAYER2, PLAYER3, PLAYER4 = range(5)

# Command Handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to the Free Fire Tournament Bot!\n"
        "Use /info to understand the process in detail.\n"
        "Use /rules to view the match rules.\n"
        "Use /register to register your team or yourself for the tournament.\n"
        "Use /schedule to view upcoming matches.\n"
        "Use /payment to complete your registration fee.\n" 
        "Use /mymatch to view your match details and get your room id.\n"
        "For any issues, contact the admin through this bot."
    )



def register(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat_id
    rescheck = requests.get(idURL, headers= headers).json()["record"]["ids"]
    if(chat_id in rescheck):
        update.message.reply_text("You Have Already Registered Using this account. Try Clearing your registration to Register Again.\n Take Care of payments before clearing your registration once unregistered you may lose your registration fee!!")
        return ConversationHandler.END
    TOURNAMENT_REGISTRATIONS["username"] =  user.username
    update.message.reply_text("Welcome! Please enter your team name.")
    return TEAM_NAME


def get_team_name(update: Update, context: CallbackContext) -> int:
    # chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS["team_name"] = update.message.text
    update.message.reply_text("Enter Player 1's username:")
    return PLAYER1


def get_player1(update: Update, context: CallbackContext) -> int:
    # chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS["player1"] = update.message.text
    update.message.reply_text("Enter Player 2's username:")
    return PLAYER2


def get_player2(update: Update, context: CallbackContext) -> int:
    # chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS["player2"] = update.message.text
    update.message.reply_text("Enter Player 3's username:")
    return PLAYER3


def get_player3(update: Update, context: CallbackContext) -> int:
    # chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS["player3"] = update.message.text
    update.message.reply_text("Enter Player 4's username:")
    return PLAYER4

def my_match(update: Update, context: CallbackContext) -> None:
    team_id = update.message.chat_id

    # Step 1: Fetch match data
    response = requests.get(matURL, headers=headers)
    if response.status_code != 200:
        update.message.reply_text("Error fetching match data. Please try again later.")
        return

    matches_data = response.json().get("record", {}).get("rounds", [])
    found_match = False

    # Step 2: Search through all matches for the team
    for match in matches_data:
        if match.get("team1_id") == team_id or match.get("team2_id") == team_id:
            found_match = True
            # Step 3: Display match details
            room_card = match.get("room_card", "No room card assigned yet.\nWait for the creator to create a room.")
            update.message.reply_text(
                f"🏆 **Match Found:**\n"
                f"🆔 Match ID: {match['match_id']}\n"
                f"🔵 Team 1: {match['team1']}\n"
                f"🔴 Team 2: {match['team2']}\n"
                f"🕒 Scheduled Time: {match['scheduled_time']}\n"
                f"🎫 Room Card: {room_card}\n"
            )

    # Step 4: If no match found
    if not found_match:
        update.message.reply_text(
            "🚫 No matches found for your Team ID.\n"
            "Keep an eye on the Telegram group for schedules and updates."
        )

def get_player4(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS["player4"] = update.message.text
    TOURNAMENT_REGISTRATIONS["id"] = chat_id
    user_data = TOURNAMENT_REGISTRATIONS

    
    logger.info(f"Data to insert: {user_data}")

    
    try:
        
        team_id = f"team_{chat_id}"  # Unique ID for the team
        response = requests.get(URL, headers=headers)
        responseof2 = requests.get(idURL, headers=headers).json()["record"]
        respids = responseof2["ids"]
        respids.append(chat_id)
        responseof2["ids"] = respids

        if response.status_code == 200:
    
            current_data = response.json()['record'] 
            # print("Current data:", current_data)
            current_data.append(user_data)

            response1 = requests.put(URL, headers=headers, json= current_data) 
            response2 = requests.put(idURL, headers= headers, json = responseof2)
            if response1.status_code == 200  & response2.status_code == 200:
                print("Data updated successfully!")
            else:
                print(f"Error: {response.status_code}")
        else:
            print(f"Error fetching data: {response.status_code}")
            
        update.message.reply_text(
            "Team registration complete! Data saved to the cloud. Use /schedule to view matches or /payment to complete registration."
        )
    except Exception as e:
        logger.error(f"Error saving to json File {e}")
        update.message.reply_text("An error occurred while saving your registration. Please try again.")

    return ConversationHandler.END
    
   



def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Registration cancelled.")
    return ConversationHandler.END


def payment(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    upreq = requests.get(idURL, headers= headers).json()["record"]
    print(upreq)
    if chat_id in upreq["ids"]:
        qr_image_path = "qr_code.png"  # Replace with your actual file path

        # Send QR code image
        with open(qr_image_path, "rb") as qr_image:
            context.bot.send_photo(
                chat_id=chat_id,
                photo=qr_image,
                caption=(
                    "Please scan this QR code using PhonePe to complete your registration fee.\n"
                    "Once payment is complete, reply with the transaction ID using:\n"
                    "`/submit_txn <Transaction_ID>`"
                ),
                parse_mode='Markdown'
            )
    else:
        update.message.reply_text("You need to register first using /register.")

def submit_txn(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    # Check if the user is registered
    upreq = requests.get(idURL, headers=headers).json()["record"]
    if chat_id not in upreq["ids"]:
        update.message.reply_text("You need to register first using /register.")
        return

    # Check if a transaction ID was provided
    if not context.args:
        update.message.reply_text("Please provide a valid transaction ID after the command. Example: /submitpayment 1234567890")
        return

    transaction_id = context.args[0]

    # Fetch player data
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        update.message.reply_text("Error fetching player data. Please try again later.")
        return

    player_data = response.json()["record"]
    player_found = False

    # Search for the player and update the transaction ID
    for player in player_data:
        if player.get("id") == chat_id:
            player["transaction_id"] = transaction_id  # Update with the provided transaction ID
            player_found = True
            break

    if not player_found:
        update.message.reply_text("No player found with your registered ID.")
        return

    # Update player data back to the server with proper payload format
    update_response = requests.put(URL, headers=headers, json= player_data)
    if update_response.status_code != 200:
        update.message.reply_text("Error updating transaction data. Please try again later.")
        return

    # Confirmation message
    update.message.reply_text("Transaction ID submitted successfully. Please wait for verification.")

# Correct command handler registration
dispatcher.add_handler(CommandHandler("submitpayment", submit_txn))



# Admin verifies payment
def verify_payment(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 2:
        update.message.reply_text("Please provide the player ID and transaction ID. Example: /verify_payment <player_id> <transaction_id>")
        return

    # Extract player ID and transaction ID from the command
    player_id = context.args[0]
    provided_txn_id = context.args[1]

    # Fetch player data from the server
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        update.message.reply_text("Error fetching player data. Please try again later.")
        return

    player_data = response.json()["record"]
    player_found = False

    # Search for the player using player_id
    for player in player_data:
        if player.get("id") == player_id:
            player_found = True
            stored_txn_id = player.get("transaction_id")

            # Verify the transaction ID
            if stored_txn_id == provided_txn_id:
                if player.get("payment") == "true":
                    update.message.reply_text("Payment is already verified for this player.")
                    return
                else:
                    player["payment"] = "true"  # Mark payment as verified

    # Update the player data back to the server
                    update_response = requests.put(URL, headers=headers, json= player_data)
                    if update_response.status_code != 200:
                        update.message.reply_text("Error updating payment verification. Please try again later.")
                        return
                    break
            else:
                update.message.reply_text("Transaction ID does not match.")
                return

    if not player_found:
        update.message.reply_text("No player found with the provided player ID.")
        return

    # Update the player data back to the server
    update_response = requests.put(URL, headers=headers, json={"record": player_data})
    if update_response.status_code != 200:
        update.message.reply_text("Error updating payment verification. Please try again later.")
        return

    # Notify admin and player about successful verification
    update.message.reply_text(f"Payment for player ID {player_id} has been verified.")
    context.bot.send_message(chat_id=int(player_id), text="Your payment has been verified! You are now officially registered for the tournament.")


def schedule(update: Update, context: CallbackContext) -> None:
    from totest import fetch_tournament_data, process_tournament

    # Step 1: Process the tournament to update data
    if TOURNAMENT_REGISTRATIONS.get("creator"):
        process_tournament()

    # Step 2: Fetch updated tournament data
    tournament_data = fetch_tournament_data()
    if not tournament_data:
        update.message.reply_text("Error fetching tournament data.")
        return

    # Step 3: Get all scheduled matches from "rounds"
    if "rounds" in tournament_data and tournament_data["rounds"]:
        matches = tournament_data["rounds"]

        # Filter upcoming matches (where the winner is still None)
        upcoming_matches = [
            match for match in matches if match.get("winner") is None
        ]

        # Step 4: Prepare the reply
        if upcoming_matches:
            match_details = "\n".join([
                f"Match {match['match_id']}: {match['team1']} vs {match['team2']} at {match['scheduled_time']} (Room: {match['match_room_id']})"
                for match in upcoming_matches
            ])
            reply_message = f"Upcoming Matches:\n\n{match_details}"
        else:
            reply_message = "All scheduled matches have been completed."
    else:
        reply_message = "No matches are scheduled at the moment."

    # Step 5: Send the reply
    update.message.reply_text(reply_message)


def clearmatch(update: Update, context: CallbackContext) -> None:
    if(TOURNAMENT_REGISTRATIONS["creator"] == True):
        
        matreq = requests.put(url= matURL, headers= headers, json = {"rounds": [],
  
  "left_out_team": None})
        update.message.reply_text(
            "Matches Cleared\n"
        )
    else:
        update.message.reply_text(
            "Players cannot clear matches\n"
        )

def assign_winner(update: Update, context: CallbackContext) -> None:
    if(TOURNAMENT_REGISTRATIONS["creator"] == True):
        
        matreq = requests.put(url= matURL, headers= headers, json = {"round_1": [],
  "round_2": [],
  "left_out_team": None})
        update.message.reply_text(
            "Matches Cleared\n"
        )
    else:
        update.message.reply_text(
            "Players cannot clear matches\n"
        )


def clearregisters(update: Update, context: CallbackContext) -> None:
    if(TOURNAMENT_REGISTRATIONS["creator"] == True):
        
        req = requests.put(url= URL, headers= headers, json = [{}])
        req2 = requests.put(url= idURL, headers= headers, json = {"ids" : [], "rc" : []})
         
        update.message.reply_text(
            "Players Registrations Cleared\n"
        )
    else:
        update.message.reply_text(
            "Players cannot clear registrations\n"
        )


def rules(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Tournament Rules:\n"
        "1. Teams must consist of 4 players.\n"
        "2. No cheating or exploiting bugs.\n"
        "3. Each match will have a specific room code provided before the match.\n"
        "4. The team leader is responsible for communication and ensuring all players are registered.\n"
        "5. Players must be available at the scheduled match time.\n"
        "6. The winner will be decided based on in-game performance and team coordination.\n"
        "7. player should not break a gloowall\n"
        "8. player are restricted to go to the top of building\n"
        "9. gerenade and other throughble items are not allowed\n"
        "10. player should face the enemies face to face , hide and back attacks are not allowed\n"
        "11. creator does not take responsibility for network ,lag and other issue\n"
        "12. Any case of Overriding RULES will result in disqualification.\n"
        "For any clarifications, please reach out to the admin.\n"       
            )


def info(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Tournament Information:\n"
        "1. To participate, use the /register command to register your team.\n"
        "2. After registration, you'll receive a payment link to complete the registration fee.\n"
        "3. Once the payment is confirmed, you will be eligible for upcoming matches.\n"
        "4. View the upcoming matches using /schedule.\n"
        "5. For any issues, contact the admin through this bot.\n"
        "Good luck to all participants!"
    )

ENTER_NAME, ENTER_PASS = range(2)
ENTER_RC = range(1)

# Function to start the creator mode process
def start_creator_mode(update: Update, context: CallbackContext) -> int:
    """Start the creator mode conversation."""
    update.message.reply_text("Creator Information:\nPlease enter your creator name:")
    return ENTER_NAME

# Function to handle the name input
def enter_name(update: Update, context: CallbackContext) -> int:
    """Handle creator name input."""
    context.user_data['name'] = update.message.text
    update.message.reply_text("Thank you! Now, please enter your password:")
    return ENTER_PASS

# Function to handle the password input and validate
def enter_password(update: Update, context: CallbackContext) -> int:
    """Validate creator credentials."""
    creator_name = context.user_data['name']
    creator_password = update.message.text

    # Fetch creator credentials
    response = requests.get(url=creURL, headers=headers)
    if response.status_code != 200:
        update.message.reply_text("Error fetching creator data. Please try again later.")
        return ConversationHandler.END

    creator_data = response.json().get('record', [])
    for creator in creator_data:
        if creator_name == creator["name"] and creator_password == creator["pass"]:
            update.message.reply_text(f"Welcome, {creator_name}! You are now in creator mode.")
            creator = True
            TOURNAMENT_REGISTRATIONS["creator"] = True
            return ConversationHandler.END

    # If credentials are invalid
    update.message.reply_text("Invalid credentials. You are not a Creator.")
    return ConversationHandler.END

# Function to handle cancellation
def cancel_creator_mode(update: Update, context: CallbackContext) -> int:
    """Cancel the creator mode process."""
    TOURNAMENT_REGISTRATIONS["creator"] = False
    update.message.reply_text("Creator mode canceled.")
    return ConversationHandler.END

def ihaverc(update: Update, context: CallbackContext) -> int:
    """Cancel the creator mode process."""
    if(TOURNAMENT_REGISTRATIONS["creator"] == True):
        update.message.reply_text("Enter The Room Id."
                                  "\nI will assign it to the appropriate TEAMs!")
        return ENTER_RC
    else:
        update.message.reply_text("You Have To Become A Creator To Conduct Matches")

def enter_rc(update: Update, context: CallbackContext) -> int:
    
    RC = int(update.message.text)
    upreq = requests.get(idURL, headers= headers).json()["record"]
    print(upreq);
    upreq["rc"].append(RC)
    update.message.reply_text("Thank you! I will add it to a team./nClick on /schedule to view the Schedule!")
    requests.put(idURL, headers=headers, json=upreq)
    totest.assign_rc()
    return ConversationHandler.END
# Define a new ConversationHandler for creator mode
creator_mode_handler = ConversationHandler(
    entry_points=[CommandHandler("creatormode", start_creator_mode)],
    states={
        ENTER_NAME: [MessageHandler(Filters.text & ~Filters.command, enter_name)],
        ENTER_PASS: [MessageHandler(Filters.text & ~Filters.command, enter_password)],
    },
    fallbacks=[CommandHandler("cancel", cancel_creator_mode)],
)

rc_Handler = ConversationHandler(
    entry_points=[CommandHandler("ihaverc", ihaverc)],
    states={
        ENTER_RC: [MessageHandler(Filters.text & ~Filters.command, enter_rc)],
    },
    fallbacks=[CommandHandler("cancel", cancel_creator_mode)],
)

def unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Sorry, I didn't understand that command.")


# Conversation Handler
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("register", register)],
    states={
        TEAM_NAME: [MessageHandler(Filters.text & ~Filters.command, get_team_name)],
        PLAYER1: [MessageHandler(Filters.text & ~Filters.command, get_player1)],
        PLAYER2: [MessageHandler(Filters.text & ~Filters.command, get_player2)],
        PLAYER3: [MessageHandler(Filters.text & ~Filters.command, get_player3)],
        PLAYER4: [MessageHandler(Filters.text & ~Filters.command, get_player4)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# Register Handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(creator_mode_handler)
dispatcher.add_handler(rc_Handler)
dispatcher.add_handler(conversation_handler)
dispatcher.add_handler(CommandHandler("payment", payment))
dispatcher.add_handler(CommandHandler("submitpayment", submit_txn))
dispatcher.add_handler(CommandHandler("verifypayment", verify_payment))
# dispatcher.add_handler(CommandHandler("payment", payment))
dispatcher.add_handler(CommandHandler("register", register))
dispatcher.add_handler(CommandHandler("mymatch", my_match))
dispatcher.add_handler(CommandHandler("schedule", schedule))

dispatcher.add_handler(CommandHandler("clearmatch", clearmatch))
dispatcher.add_handler(CommandHandler("clearregisters", clearregisters))
dispatcher.add_handler(CommandHandler("rules", rules))  # Add the rules handler
dispatcher.add_handler(CommandHandler("info", info)) 
dispatcher.add_handler(CommandHandler("creatormode", start_creator_mode)) 
dispatcher.add_handler(CommandHandler("ihaverc", ihaverc)) 
dispatcher.add_handler(CommandHandler("nocreatormode", cancel_creator_mode)) 
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Flask Webhook Route
@app.route("/<bot_token>", methods=["POST"])
def webhook(bot_token):
    if bot_token != BOT_TOKEN:
        return "Invalid token", 400
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "OK"
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return "Internal Server Error", 500


# Main Entry Point
if __name__ == "__main__":
    app.run(port=5000)
