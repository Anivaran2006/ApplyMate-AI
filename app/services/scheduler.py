from apscheduler.schedulers.background import BackgroundScheduler

from app.services.monitor import monitor

scheduler = BackgroundScheduler()

def start_scheduler():

    scheduler.add_job(
        monitor,
        "interval",
       seconds=30
    )

    scheduler.start()

    print("ApplyMate Scheduler Started")