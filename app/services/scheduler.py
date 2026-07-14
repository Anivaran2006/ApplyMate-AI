from apscheduler.schedulers.background import BackgroundScheduler

from app.services.monitor import monitor

scheduler = BackgroundScheduler()


def start_scheduler():

    if scheduler.running:
        return

    scheduler.add_job(
        monitor,
        trigger="interval",
        minutes=30,              # Every 30 minutes during development
        id="applymate_monitor",
        replace_existing=True,
        max_instances=1
    )

    scheduler.start()

    print("=" * 50)
    print("✅ ApplyMate AI Scheduler Started")
    print("⏰ Running every 30 minutes")
    print("=" * 50)

    # Run once immediately when the server starts
    print("🚀 Running first scan...")
    monitor()