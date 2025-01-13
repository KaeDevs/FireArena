# 7592940575:AAFtJnf4DqUeKtVdfmPx_d4wqbf3lwYOlCM

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global Variables
TOURNAMENT_REGISTRATIONS = {}  # Dictionary to store registrations

# Commands
def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message and instructions."""
    update.message.reply_text(
        "Welcome to the Free Fire Tournament Bot!\n"
        "Use /register to register your team or yourself for the tournament.\n"
        "Use /schedule to view upcoming matches.\n"
        "Use /payment to complete your registration fee.\n"
        "For any issues, contact the admin through this bot."
    )

def register(update: Update, context: CallbackContext) -> None:
    """Register a team or player."""
    user = update.message.from_user
    chat_id = update.message.chat_id

    # Ask for team/player name
    update.message.reply_text(
        "Please provide your team name or player name for registration:"
    )
    TOURNAMENT_REGISTRATIONS[chat_id] = {"user_id": user.id, "username": user.username}

def save_registration(update: Update, context: CallbackContext) -> None:
    """Save the team or player name."""
    chat_id = update.message.chat_id
    if chat_id in TOURNAMENT_REGISTRATIONS:
        TOURNAMENT_REGISTRATIONS[chat_id]["team_name"] = update.message.text
        update.message.reply_text(
            f"Thank you! Team/Player '{update.message.text}' has been registered.\n"
            "Use /payment to complete the registration."
        )
    else:
        update.message.reply_text("Please start registration using /register first.")

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

def unknown(update: Update, context: CallbackContext) -> None:
    """Handle unknown commands."""
    update.message.reply_text("Sorry, I didn't understand that command.")

# Main Function
def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_BOT_TOKEN' with the token you got from BotFather
    BOT_TOKEN = "7592940575:AAFtJnf4DqUeKtVdfmPx_d4wqbf3lwYOlCM"

    # Create the Updater and pass it your bot's token
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("payment", payment))
    dispatcher.add_handler(CommandHandler("schedule", schedule))

    # Message handler for team/player name during registration
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, save_registration))

    # Unknown commands
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
