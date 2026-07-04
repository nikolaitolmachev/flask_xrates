import logging
import traceback

import importlib
import requests

from ..config import HTTP_TIMEOUT
from ..models import XRate, peewee_datetime, ApiLog, ErrorLog


log = logging.getLogger(__name__)


def update_rate(from_currency, to_currency):
    xrate = XRate.select().where(
        XRate.from_currency == from_currency, XRate.to_currency == to_currency
    ).first()

    if not xrate:
        raise ValueError(f"Unknown currency pair: {from_currency} => {to_currency}")

    module = importlib.import_module(f"app.api.{xrate.module}")
    module.Api().update_rate(xrate)


class _Api:
    def __init__(self, logger_name):
        self.log = logging.getLogger(logger_name)

    def update_rate(self, xrate):
        self.log.info("Started update for: %s", xrate)

        self.log.debug("rate before: %s", xrate)
        xrate.rate = self._update_rate(xrate)
        xrate.updated = peewee_datetime.datetime.now()
        xrate.save()

        self.log.debug("rate after: %s", xrate)
        self.log.info("Finished update for: %s", xrate)

    def _update_rate(self, xrate):
        raise NotImplementedError("_update_rate")

    def _send_request(self, url, method, data=None, headers=None):
        api_log = ApiLog(request_url=url, request_data=data, request_method=method, request_headers=headers)
        try:
            response = self._send(method=method, url=url, headers=headers, data=data)
            api_log.response_text = response.text
            return response
        except Exception as ex:
            self.log.exception("Error during request sending")
            api_log.error = str(ex)
            ErrorLog.create(
                request_data=data, request_url=url, request_method=method,
                error=str(ex), traceback=traceback.format_exc(chain=False)
            )
            raise
        finally:
            api_log.finished = peewee_datetime.datetime.now()
            api_log.save()

    @staticmethod
    def _send(url, method, data=None, headers=None):
        return requests.request(method=method, url=url, headers=headers, data=data, timeout=HTTP_TIMEOUT)
