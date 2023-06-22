from flask import Flask, request, jsonify
import stripe
import os
from dotenv import load_dotenv
from common import send_email_to_user, load_user_map
from telegram import Bot


load_dotenv()

# Define constants
stripe.api_key = os.getenv("STRIPE_API_KEY")
sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
user_map_file = os.getenv("USER_MAP_FILE")
channel_id = os.getenv("CHANNEL_ID")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

# Create an instance of the Bot
bot = Bot(token=telegram_bot_token)

# Flask app
app = Flask(__name__)


@app.route("/stripe", methods=["POST"])
def stripe_webhook():
    event = stripe.Event.construct_from(request.get_json(), stripe.api_key)
    if event.type == "customer.subscription.created":
        print("Subscription created")
        customer_id = event.data.object.customer
        customer = stripe.Customer.retrieve(customer_id)
        print(f"Customer email: {customer.email}")
        send_email_to_user(customer_id, customer.email)
    elif event.type == "customer.subscription.deleted":
        print("Subscription deleted")
        customer_id = event.data.object.customer
        user_map = load_user_map()
        if customer_id in user_map:
            print("Banning user:" + customer_id + " from channel")
            telegram_id = user_map[customer_id]
            bot.ban_chat_member(chat_id=channel_id, user_id=telegram_id)
    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        if subscription.status == "active":
            print("Subscription reactivated")
            customer_id = event.data.object.customer
            customer = stripe.Customer.retrieve(customer_id)
            user_map = load_user_map()
            if customer_id in user_map:
                print("Unbanning user:" + customer_id + " from channel")
                telegram_id = user_map[customer_id]
                bot.unban_chat_member(chat_id=channel_id, user_id=telegram_id)
                send_email_to_user(customer_id, customer.email)
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(port=3000)
