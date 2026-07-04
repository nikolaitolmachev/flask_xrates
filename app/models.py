import logging

from peewee import (
    SqliteDatabase, Model, IntegerField, DoubleField, DateTimeField, CharField, TextField, datetime as peewee_datetime
)

from .config import DB_NAME


log = logging.getLogger(__name__)

db = SqliteDatabase(DB_NAME)


class _Model(Model):
    id = IntegerField(primary_key=True)

    class Meta:
        database = db


class XRate(_Model):
    class Meta:
        db_table = "xrates"
        indexes = (
            (("from_currency", "to_currency"), True),
        )

    from_currency = IntegerField()
    to_currency = IntegerField()
    rate = DoubleField()
    updated = DateTimeField(default=peewee_datetime.datetime.now)
    module = CharField(max_length=100)

    def __str__(self):
        return "XRate(%s=>%s): %s" % (self.from_currency, self.to_currency, self.rate)


class ApiLog(_Model):
    class Meta:
        db_table = "api_logs"

    request_url = CharField()
    request_data = TextField(null=True)
    request_method = CharField(max_length=100)
    request_headers = TextField(null=True)
    response_text = TextField(null=True)
    created = DateTimeField(index=True, default=peewee_datetime.datetime.now)
    finished = DateTimeField()
    error = TextField(null=True)

    def json(self):
        return {
            "id": self.id,
            "request_url": self.request_url,
            "request_method": self.request_method,
            "created": str(self.created),
            "finished": str(self.finished),
            "error": self.error,
        }


class ErrorLog(_Model):
    class Meta:
        db_table = "error_logs"

    request_data = TextField(null=True)
    request_url = TextField()
    request_method = CharField(max_length=100)
    error = TextField()
    traceback = TextField(null=True)
    created = DateTimeField(default=peewee_datetime.datetime.now, index=True)


def create_tables():
    """Create tables if they don't exist, seed default rates if empty."""
    db.create_tables([XRate, ApiLog, ErrorLog], safe=True)

    if XRate.select().count() == 0:
        XRate.create(from_currency=840, to_currency=933, rate=1, module="nbrbby_api")
        XRate.create(from_currency=978, to_currency=933, rate=1, module="nbrbby_api")
        XRate.create(from_currency=1000, to_currency=840, rate=1, module="crypto_api")
        XRate.create(from_currency=1000, to_currency=978, rate=1, module="crypto_api")
        XRate.create(from_currency=1000, to_currency=933, rate=1, module="crypto_api")
        log.info("Database seeded with default rates")

    log.info("Database ready: %s", DB_NAME)


def init_db():
    """Drop all tables and recreate from scratch (development only)."""
    for m in (XRate, ApiLog, ErrorLog):
        m.drop_table()
        m.create_table()

    XRate.create(from_currency=840, to_currency=933, rate=1, module="nbrbby_api")
    XRate.create(from_currency=978, to_currency=933, rate=1, module="nbrbby_api")
    XRate.create(from_currency=1000, to_currency=840, rate=1, module="crypto_api")
    XRate.create(from_currency=1000, to_currency=978, rate=1, module="crypto_api")
    XRate.create(from_currency=1000, to_currency=933, rate=1, module="crypto_api")

    log.info("Database reset: %s", DB_NAME)
