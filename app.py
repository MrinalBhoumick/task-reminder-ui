import os
import schedule
import time
from datetime import datetime
import streamlit as st
from twilio.rest import Client
from dotenv import load_dotenv
import pytz

# Load environment variables from .env file
load_dotenv()

# Fetch credentials from environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
whatsapp_from = os.getenv("WHATSAPP_FROM")

# Initialize Twilio client
if not account_sid or not auth_token:
    st.error("Twilio credentials are not set in the environment variables.")
    st.stop()

client = Client(account_sid, auth_token)

# Function to send WhatsApp message
def send_whatsapp_message(to, body):
    try:
        message = client.messages.create(
            from_=whatsapp_from,
            body=body,
            to=to
        )
        return message.sid
    except Exception as e:
        st.error(f"Failed to send reminder: {str(e)}")
        return None

# Function to schedule a reminder
def schedule_reminder(to, body, reminder_time):
    def job():
        send_whatsapp_message(to, body)

    schedule.every().day.at(reminder_time.strftime("%H:%M")).do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Streamlit UI
st.title("WhatsApp Reminder App")

# Input fields for user
to = st.text_input("Enter recipient's WhatsApp number (e.g., +91XXXXXXXXXX):")
message_body = st.text_area("Enter your reminder message:")
reminder_date = st.date_input("Select the date for the reminder")
reminder_time = st.time_input("Select the time for the reminder (IST)")

# Submit button
if st.button("Set Reminder"):
    if not to or not message_body:
        st.error("Please enter a valid WhatsApp number and message.")
    else:
        # Combine date and time into a single datetime object
        reminder_datetime = datetime.combine(reminder_date, reminder_time, tzinfo=pytz.timezone("Asia/Kolkata"))

        if reminder_datetime < datetime.now(pytz.timezone("Asia/Kolkata")):
            st.error("Reminder time must be in the future.")
        else:
            st.success("Reminder has been set!")
            st.write(f"Reminder will be sent to {to} on {reminder_datetime}.")
            # Schedule the reminder (run in a separate thread in production code)
            schedule_reminder(to, message_body, reminder_datetime)
