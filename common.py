import sqlite3
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

# Define constants
sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
database_file = os.getenv("USER_MAP_FILE")


# Function to get connection to SQLite database
def get_db_connection():
    conn = sqlite3.connect(database_file)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS user_map (customer_id TEXT, telegram_id TEXT)"
    )
    return conn


# Function to load user_map from database
def load_user_map():
    conn = get_db_connection()
    cursor = conn.execute("SELECT customer_id, telegram_id FROM user_map")
    return {row[0]: row[1] for row in cursor.fetchall()}


# Function to save user_map to database
def save_user_map(user_map):
    conn = get_db_connection()
    conn.execute("DELETE FROM user_map")  # Clear old data
    for customer_id, telegram_id in user_map.items():
        conn.execute(
            "INSERT INTO user_map (customer_id, telegram_id) VALUES (?, ?)",
            (customer_id, telegram_id),
        )
    conn.commit()


# Function to send email using SendGrid
def send_email_to_user(customer_id, customer_email):
    message = Mail(
        from_email="human@whoneedshumans.com",
        to_emails=customer_email,
        subject="Link your Telegram account",
        plain_text_content=f"Click this link to link your Telegram account: https://t.me/WNHMembershipBot?start={customer_id}",
    )
    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Sent email to {customer_email}. Response code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending email: {e.message}")
