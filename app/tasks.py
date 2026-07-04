import logging
from logging.config import dictConfig

from apscheduler.schedulers.blocking import BlockingScheduler

from . import api
from .config import LOGGER_CONFIG
from .models import XRate


log = logging.getLogger("Tasks")


def run_scheduler():
    dictConfig(LOGGER_CONFIG)

    sched = BlockingScheduler()

    @sched.scheduled_job("interval", minutes=10)
    def update_rates():
        log.info("Job started")
        xrates = XRate.select()
        for rate in xrates:
            try:
                api.update_rate(rate.from_currency, rate.to_currency)
            except Exception as ex:
                log.exception(ex)
        log.info("Job finished")

    log.info("Scheduler started")
    sched.start()


if __name__ == '__main__':
    run_scheduler()
