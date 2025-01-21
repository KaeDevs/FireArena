from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from flask import Flask, request
import logging
from pymongo import MongoClient
import telegram

# Flask app
app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7592940575:AAFtJnf4DqUeKtVdfmPx_d4wqbf3lwYOlCM"
bot = Bot(token=BOT_TOKEN)

client = MongoClient("mongodb+srv://mkavin2005:hqr5SqhrHI3diFn1@fireplay.dkbtt.mongodb.net/?retryWrites=true&w=majority&appName=FirePlay")
db = client["FirePlay"]  # Replace with your database name
players_collection = db["players"]

# Initialize Application (instead of Dispatcher)
application = Application.builder().token(BOT_TOKEN).build()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global Variables
TOURNAMENT_REGISTRATIONS = {}  # Dictionary to store registrations

# Conversation steps
TEAM_NAME, PLAYER1, PLAYER2, PLAYER3, PLAYER4 = range(5)

# Command Handlers
def start(update: Update, context: CallbackContext) -> int:
    """Send a welcome message and instructions."""
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
    """Start the registration process for a team or player."""
    user = update.message.from_user
    chat_id = update.message.chat_id

    # Store initial user info
    TOURNAMENT_REGISTRATIONS[chat_id] = {"user_id": user.id, "username": user.username}
    update.message.reply_text("Welcome! Please enter your team name.")
    return TEAM_NAME

def get_team_name(update: Update, context: CallbackContext) -> int:
    """Get the team name."""
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS[chat_id]["team_name"] = update.message.text
    update.message.reply_text("Enter Player 1's username:")
    return PLAYER1

def get_player1(update: Update, context: CallbackContext) -> int:
    """Get Player 1's username."""
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS[chat_id]["player1"] = update.message.text
    update.message.reply_text("Enter Player 2's username:")
    return PLAYER2

def get_player2(update: Update, context: CallbackContext) -> int:
    """Get Player 2's username."""
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS[chat_id]["player2"] = update.message.text
    update.message.reply_text("Enter Player 3's username:")
    return PLAYER3

def get_player3(update: Update, context: CallbackContext) -> int:
    """Get Player 3's username."""
    chat_id = update.message.chat_id
    TOURNAMENT_REGISTRATIONS[chat_id]["player3"] = update.message.text
    update.message.reply_text("Enter Player 4's username:")
    return PLAYER4

def get_player4(update: Update, context: CallbackContext) -> int:
    """Get Player 4's username and complete registration."""
    chat_id = update.message.chat_id
    user_data = TOURNAMENT_REGISTRATIONS[chat_id]
    user_data["player4"] = update.message.text

    # Prepare data for MongoDB
    data = {
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        "team_name": user_data["team_name"],
        "players": [
            user_data["player1"],
            user_data["player2"],
            user_data["player3"],
            user_data["player4"]
        ]
    }

    # Insert into MongoDB
    players_collection.insert_one(data)

    update.message.reply_text("Your team has been registered successfully!")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the registration process."""
    update.message.reply_text("Registration cancelled.")
    return ConversationHandler.END

def payment(update: Update, context: CallbackContext) -> None:
    """Send the payment link."""
    chat_id = update.message.chat_id
    if chat_id in TOURNAMENT_REGISTRATIONS:
        payment_link = "https://example.com/payment-link"  # Replace with your UPI/Razorpay link
        update.message.reply_text(
            f"Please complete your registration fee using this link:\n{payment_link}\n"
            "Once payment is complete, reply with the transaction ID."
        )
    else:
        update.message.reply_text("You need to register first using /register.")

def schedule(update: Update, context: CallbackContext) -> None:
    """Show the match schedule."""
    update.message.reply_text(
        "Upcoming Matches:\n"
        "1. Match 1: Jan 15, 6 PM (Room Code: XYZ123)\n"
        "2. Match 2: Jan 16, 6 PM (Room Code: ABC456)\n"
        "Stay tuned for more updates!"
    )

def rules(update: Update, context: CallbackContext) -> None:
    """Show the rules of the match."""
    update.message.reply_text(
        "Match Rules:\n"
        "1. No use of hacks or third-party software.\n"
        "2. Teams must join the room 10 minutes before the match.\n"
        "3. Players who disconnect during the match will not be allowed to rejoin.\n"
        "4. Abusive language and unsportsmanlike behavior will result in disqualification.\n"
        "5. Admin decisions are final in all disputes.\n"
        "Play fair and enjoy the tournament!"
    )

def info(update: Update, context: CallbackContext) -> None:
    """Explain the tournament process."""
    update.message.reply_text(
        "Tournament Process:\n"
        "1. Use /register to register your team or yourself.\n"
        "2. After registration, complete the registration fee using /payment.\n"
        "3. Once payment is confirmed, you will receive match details and the room code.\n"
        "4. Join the match at the scheduled time using the room code provided.\n"
        "5. Keep track of your progress through this bot, and use /schedule to check future matches.\n"
        "For any issues, contact the admin through this bot.\n\n"
        "Good luck and have fun!"
    )

def unknown(update: Update, context: CallbackContext) -> None:
    """Handle unknown commands."""
    update.message.reply_text("Sorry, I didn't understand that command.")

# Register ConversationHandler for multi-step registration
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

# Register Handlers with Application
application.add_handler(CommandHandler("start", start))
application.add_handler(conversation_handler)
application.add_handler(CommandHandler("payment", payment))
application.add_handler(CommandHandler("schedule", schedule))
application.add_handler(CommandHandler("rules", rules))
application.add_handler(CommandHandler("info", info))
application.add_handler(MessageHandler(Filters.command, unknown))

# Flask Webhook Route
@app.route('/<bot_token>', methods=['POST'])
def webhook(bot_token):
    if bot_token != BOT_TOKEN:
        return "Invalid token", 400
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        application.process_update(update)  # Process the update using application
        return 'OK'
    except Exception as e:
        print(f"Error processing update: {e}")
        return 'Internal Server Error', 500

# Main Entry Point
if __name__ == "__main__":
    app.run(port=5000)
