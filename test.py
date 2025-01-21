from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from flask import Flask, request
import logging
from pymongo import MongoClient, errors
import telegram

# Flask app
app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7592940575:AAFtJnf4DqUeKtVdfmPx_d4wqbf3lwYOlCM"
bot = Bot(token=BOT_TOKEN)

# MongoDB Configuration
try:
    client = MongoClient(
        "mongodb+srv://mkavin2005:hqr5SqhrHI3diFn1@fireplay.dkbtt.mongodb.net/?retryWrites=true&w=majority&appName=FirePlay"
    )
    db = client["FirePlay"]  # Replace with your database name
    players_collection = db["players"]
    print("Connected to MongoDB successfully!")
except errors.ConnectionError as e:
    print(f"Failed to connect to MongoDB: {e}")
    exit()

# Updater and Dispatcher
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Global Variables
TOURNAMENT_REGISTRATIONS = {}  # Dictionary to store registrations

# Conversation steps
TEAM_NAME, PLAYER1, PLAYER2, PLAYER3, PLAYER4 = range(5)

# Command Handlers
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Welcome to the Free Fire Tournament Bot!\n"
        "Use /register to register your team or yourself for the tournament.\n"
        "Use /schedule to view upcoming matches.\n"
        "Use /payment to complete your registration fee.\n"
        "Use /rules to view the match rules.\n"
        "Use /info to understand the process in detail.\n"
        "For any issues, contact the admin through this bot."
    )


def register(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chat_id = update.message.chat_id

    TOURNAMENT_REGISTRATIONS[chat_id] = {"user_id": user.id, "username": user.username}
    update.message.reply_text("Welcome! Please enter your team name.")
    return TEAM_NAME


def get_team_name(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS[chat_id]["team_name"] = update.message.text
    update.message.reply_text("Enter Player 1's username:")
    return PLAYER1


def get_player1(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS[chat_id]["player1"] = update.message.text
    update.message.reply_text("Enter Player 2's username:")
    return PLAYER2


def get_player2(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS[chat_id]["player2"] = update.message.text
    update.message.reply_text("Enter Player 3's username:")
    return PLAYER3


def get_player3(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS[chat_id]["player3"] = update.message.text
    update.message.reply_text("Enter Player 4's username:")
    return PLAYER4


def get_player4(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    user_data = TOURNAMENT_REGISTRATIONS[chat_id]
    user_data["player4"] = update.message.text

    # Debugging: Print the data to be inserted into MongoDB
    logger.info(f"Data to insert: {user_data}")

    # Attempt to save data to MongoDB
    try:
        # Check if the user data is in the expected format
        if not all(key in user_data for key in ["team_name", "player1", "player2", "player3", "player4"]):
            raise ValueError("Missing required player information.")

        players_collection.insert_one(user_data)
        update.message.reply_text(
            "Team registration complete! You can use /schedule to view upcoming matches or /payment to complete your registration fee."
        )
    except ValueError as ve:
        # Handle validation errors, e.g., missing player data
        logger.error(f"Validation Error: {ve}")
        update.message.reply_text("Incomplete team registration. Please ensure all players' usernames are provided.")
    except errors.ConnectionError as ce:
        # Handle MongoDB connection errors
        logger.error(f"MongoDB Connection Error: {ce}")
        update.message.reply_text("Could not connect to the database. Please try again later.")
    except Exception as e:
        # General error handling
        logger.error(f"Failed to save registration to database: {e}")
        update.message.reply_text("An error occurred while saving your registration. Please try again.")
    
    return ConversationHandler.END



def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Registration cancelled.")
    return ConversationHandler.END


def payment(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    if chat_id in TOURNAMENT_REGISTRATIONS:
        payment_link = "https://example.com/payment-link"
        update.message.reply_text(
            f"Please complete your registration fee using this link:\n{payment_link}\n"
            "Once payment is complete, reply with the transaction ID."
        )
    else:
        update.message.reply_text("You need to register first using /register.")


def schedule(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Upcoming Matches:\n"
        "1. Match 1: Jan 15, 6 PM (Room Code: XYZ123)\n"
        "2. Match 2: Jan 16, 6 PM (Room Code: ABC456)\n"
        "Stay tuned for more updates!"
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
        "For any clarifications, please reach out to the admin."
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
dispatcher.add_handler(conversation_handler)
dispatcher.add_handler(CommandHandler("payment", payment))
dispatcher.add_handler(CommandHandler("schedule", schedule))
dispatcher.add_handler(CommandHandler("rules", rules))  # Add the rules handler
dispatcher.add_handler(CommandHandler("info", info)) 
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
