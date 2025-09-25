

import sqlite3
from datetime import datetime, time as dtime, timezone, timedelta
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler


def start_scheduler(send_func, db_path: str, self_handle: str, tz_name="America/Toronto"):
    tz = ZoneInfo(tz_name)
    sched = BackgroundScheduler(timezone=tz)

    # 9:00 gym check (you already have this)
    sched.add_job(gym_check, trigger="cron", hour=9, minute=0, id="gym_daily_9")

    # 9:30 second nudge if no pic yet
    def gym_second_nudge():
        if not _sent_image_to_self_today(db_path, self_handle, tz):
            send_func(self_handle, "⏳ 9:30 check — still waiting on that gym pic 💪")
    sched.add_job(gym_second_nudge, "cron", hour=9, minute=30, id="gym_daily_930")

    # Example: 8:00 “morning agenda”
    def morning_agenda():
        send_func(self_handle, "☀️ Morning check-in — what’s the plan today?")
    sched.add_job(morning_agenda, "cron", hour=8, minute=0, id="morning_agenda")

    sched.start()
    return sched
