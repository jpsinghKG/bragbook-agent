"""Runs the collection pipeline on a daily timer.

Only collects and upserts to the store -- no redaction or summarization.
Those happen on demand when the user runs main.py.
"""

import time

import schedule
from dotenv import load_dotenv

import collect
from config.settings import Settings

load_dotenv()

settings = Settings()


def job() -> None:
    since, until = collect.run(settings)
    print(f"collected events from {since} to {until}")


if __name__ == "__main__":
    schedule.every().day.at(settings.app.schedule_time).do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)
