from functools import wraps

from flask import request, abort

from . import controllers
from .config import IP_LIST


def check_ip(func):
    @wraps(func)
    def checker(*args, **kwargs):
        if request.remote_addr not in IP_LIST:
            return abort(403)
        return func(*args, **kwargs)
    return checker


def init_app(app):
    app.add_url_rule("/", "view_rates", lambda: controllers.ViewAllRates().call())

    app.add_url_rule("/api/xrates/<fmt>", 'api_rates', lambda fmt: controllers.GetApiRates().call(fmt))

    app.add_url_rule(
        "/update/<int:from_currency>/<int:to_currency>", "update_xrates_pair",
        lambda from_currency, to_currency: controllers.UpdateRates().call(from_currency, to_currency)
    )

    app.add_url_rule(
        "/update/all", "update_xrates_all",
        lambda: controllers.UpdateRates().call(None, None)
    )

    app.add_url_rule(
        "/edit/<int:from_currency>/<int:to_currency>", "edit_xrate",
        check_ip(lambda from_currency, to_currency: controllers.EditRate().call(from_currency, to_currency)),
        methods=["GET", "POST"]
    )

    app.add_url_rule("/logs", "view_logs", check_ip(lambda: controllers.ViewLogs().call()))
