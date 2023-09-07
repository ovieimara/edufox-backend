from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


# Schedule a task to run every minute
# scheduler.add_job(my_background_task, trigger=CronTrigger(minute=2))
scheduler = BackgroundScheduler()


def start():
    # from myapp.tasks import my_task  # Import here to avoid AppRegistryNotReady
    from autocomplete.tasks import my_background_task

    # Schedule a task to run every minute
    scheduler.add_job(my_background_task, 'interval', minutes=2)
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()
