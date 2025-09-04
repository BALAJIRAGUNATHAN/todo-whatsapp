from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from app import db, client, TWILIO_WHATSAPP
from models import Task, User
from app import app

def process_due_tasks():
    """Send WhatsApp reminders for due tasks."""
    with app.app_context():
        now = datetime.now(timezone.utc)  # Current UTC time
        tasks = Task.query.filter(
            Task.due_date <= now,
            Task.whatsapp == True,
            Task.completed == False
        ).all()

        for task in tasks:
            user = User.query.get(task.user_id)
            if user and user.whatsapp_number:
                message = client.messages.create(
                    from_=TWILIO_WHATSAPP,
                    body=f"⏰ Reminder: '{task.title}' is due!",
                    to=f"whatsapp:{user.whatsapp_number}"
                )
                print(f"WhatsApp message sent! SID: {message.sid}")  # Print SID for debugging

def start_scheduler():
    sched = BackgroundScheduler()
    sched.add_job(process_due_tasks, "interval", minutes=1)  # Check every minute
    sched.start()

if __name__ == "__main__":
    start_scheduler()
    import time
    while True:
        time.sleep(3600)  # Keep running
