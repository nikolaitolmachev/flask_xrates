from models import XRate, peewee_datetime

from config import LOGGER_CONFIG, logging

log = logging.getLogger('TestApi')
fh = logging.FileHandler(LOGGER_CONFIG['file'])
fh.setLevel(LOGGER_CONFIG['level'])
fh.setFormatter(LOGGER_CONFIG['formatter'])
log.addHandler(fh)
log.setLevel(LOGGER_CONFIG['level'])

def update_xrates(from_currency: int, to_currency: int):
    log.info('Started update for: %s=>%s' % (from_currency, to_currency))
    xrate = XRate.select().where(XRate.from_currency == from_currency and XRate.to_currency == to_currency).first()

    log.debug('rate before: %s', xrate)
    xrate.rate += 1
    xrate.updated = peewee_datetime.datetime.now()
    xrate.save()

    log.debug('rate after: %s', xrate)
    log.info('Finished update for: %s=>%s' % (from_currency, to_currency))