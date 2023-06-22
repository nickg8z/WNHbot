from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, Updater, CommandHandler, CallbackContext
import asyncio
from common import load_user_map, save_user_map
import os
from dotenv import load_dotenv

load_dotenv()

# Define constants
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
channel_id = os.getenv("CHANNEL_ID")

# Create an instance of the Bot
bot = Bot(token=telegram_bot_token)


# Create an asyncio Queue for the updates
update_queue = asyncio.Queue()

# Create the Updater
updater = Updater(bot, update_queue)


# Store a map of Stripe customer ID to Telegram ID
# Store a map of Stripe customer ID to Telegram ID in a text file
user_map_file = "user_map.txt"


async def start(update: Update, context: CallbackContext) -> None:
    print("Start called by user:")
    user = update.effective_user
    print(user)
    # Get an invite link to the channel
    chat_link = await bot.create_chat_invite_link(chat_id=channel_id)
    # Get the customer ID from the command arguments.
    if context.args:
        customer_id = context.args[0]
        user_map = load_user_map()
        user_map[customer_id] = user.id
        save_user_map(user_map)
        await update.message.reply_text(
            f"Linked your Telegram account with your Who Needs Humans account."
            f"\n\n"
            f"Click here to join the private chat: {chat_link.invite_link}"
        )
        print(f"Linked {customer_id} to {user.id}")
    else:
        await update.message.reply_text(
            "Please provide a WNH customer ID as a command argument. If you do not have one please contact WNH support."
        )


if __name__ == "__main__":
    application = (
        ApplicationBuilder()
        .token("6284296736:AAFl74WzYyw5iWsNjNGM-Abq-rMTJf0eGKk")
        .build()
    )

    # start_handler = CommandHandler("start", start)

    application.add_handler(CommandHandler(["start"], start))

    print("Adding handler")
    print("Starting bot polling")
    application.run_polling()

    print("Running...")
