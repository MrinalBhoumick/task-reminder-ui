import streamlit as st
import schedule
import time
from datetime import datetime
import pytz
from twilio.rest import Client
from dotenv import load_dotenv
import os
import threading


load_dotenv()

# Twilio credentials from .env
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
whatsapp_from = os.getenv('WHATSAPP_FROM')


client = Client(account_sid, auth_token)


def send_whatsapp_message(message_body, recipients):
    for recipient in recipients:
        try:
            message = client.messages.create(
                body=message_body,
                from_=whatsapp_from,
                to=recipient.strip()
            )
            print(f"Reminder sent successfully to {recipient}! Message SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send reminder to {recipient}: {e}")


def schedule_reminder(date_str, time_str, message_body, recipients):
    try:
        ist = pytz.timezone('Asia/Kolkata')
        reminder_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        reminder_datetime = ist.localize(reminder_datetime)

        # Calculate time delay
        delay_seconds = (reminder_datetime - datetime.now(ist)).total_seconds()

        if delay_seconds <= 0:
            st.warning("The scheduled time is in the past. Please select a future time.")
            return

        
        schedule.every(delay_seconds).seconds.do(send_whatsapp_message, message_body=message_body, recipients=recipients)
        st.success("Reminder set successfully!")
        print(f"Reminder scheduled for {reminder_datetime} to recipients: {recipients}")
    except Exception as e:
        print(f"Error scheduling reminder: {e}")
        st.error("Failed to set reminder. Check date and time format.")


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


st.title("WhatsApp Reminder (IST)")

st.write("Please set the date and time in Indian Standard Time (IST).")

with st.form("reminder_form"):
    date_str = st.date_input("Select Date")
    time_str = st.time_input("Select Time (24-hour format, IST)").strftime("%H:%M")
    message_body = st.text_area("Message")
    recipients = st.text_area("Enter recipient numbers (comma-separated, in +91 format)", placeholder="+91123XXXXXXXX, +91987XXXXXXX")

    
    if st.form_submit_button("Set Reminder"):
        if not date_str or not time_str or not message_body or not recipients:
            st.warning("Please fill in all fields.")
        else:
            recipient_list = [num.strip() for num in recipients.split(',') if num.strip()]
            schedule_reminder(date_str.strftime("%Y-%m-%d"), time_str, message_body, recipient_list)

if 'scheduler_thread' not in st.session_state:
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    st.session_state['scheduler_thread'] = scheduler_thread
