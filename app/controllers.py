import datetime
import logging

import xmltodict
from flask import render_template, make_response, jsonify, request, redirect, url_for

from . import api
from .config import CODE_CURRENCY
from .models import XRate, ApiLog


log = logging.getLogger(__name__)


class BaseController:
    def __init__(self):
        self.request = request

    def call(self, *args, **kwargs):
        try:
            return self._call(*args, **kwargs)
        except Exception as ex:
            log.exception("Controller error: %s", ex)
            return make_response("Internal server error", 500)

    def _call(self, *args, **kwargs):
        raise NotImplementedError("_call")


class ViewAllRates(BaseController):
    def _call(self):
        xrates = XRate.select()
        return render_template("xrates.html", xrates=xrates, codes=CODE_CURRENCY)


class GetApiRates(BaseController):
    def _call(self, fmt):
        xrates = XRate.select()
        xrates = self._filter(xrates)

        if fmt == "json":
            return self._get_json(xrates)
        elif fmt == "xml":
            return self._get_xml(xrates)
        raise ValueError(f"Unknown format: {fmt}")

    def _filter(self, xrates):
        args = self.request.args

        if "from_currency" in args:
            xrates = xrates.where(XRate.from_currency == args["from_currency"])

        if "to_currency" in args:
            xrates = xrates.where(XRate.to_currency == args.get("to_currency"))

        return xrates

    @staticmethod
    def _get_xml(xrates):
        d = {"xrates": {"xrate": [
            {"from": rate.from_currency, "to": rate.to_currency, "rate": rate.rate} for rate in xrates]}}
        return make_response(xmltodict.unparse(d), {"Content-Type": "text/xml"})

    @staticmethod
    def _get_json(xrates):
        return jsonify([{"from": rate.from_currency, "to": rate.to_currency, "rate": rate.rate} for rate in xrates])


class UpdateRates(BaseController):
    def _call(self, from_currency, to_currency):
        if not from_currency and not to_currency:
            self._update_all()

        elif from_currency and to_currency:
            self._update_rate(from_currency, to_currency)

        else:
            raise ValueError("from_currency and to_currency")
        return redirect(url_for("view_rates"))

    @staticmethod
    def _update_rate(from_currency, to_currency):
        api.update_rate(from_currency, to_currency)

    def _update_all(self):
        xrates = XRate.select()
        for rate in xrates:
            try:
                self._update_rate(rate.from_currency, rate.to_currency)
            except Exception as ex:
                log.exception("Update failed for %s: %s", rate, ex)


class ViewLogs(BaseController):
    def _call(self):
        try:
            page = int(self.request.args.get("page", 1))
            if page < 1:
                raise ValueError
        except (ValueError, TypeError):
            page = 1
        logs = ApiLog.select().paginate(page, 10).order_by(ApiLog.id.desc())
        return render_template("logs.html", logs=logs)


class EditRate(BaseController):
    def _call(self, from_currency, to_currency):
        if self.request.method == "GET":
            return render_template("rate_edit.html",
                                   from_currency=from_currency, to_currency=to_currency,
                                   from_code=CODE_CURRENCY.get(from_currency, from_currency),
                                   to_code=CODE_CURRENCY.get(to_currency, to_currency))

        # POST request is got
        if "new_rate" not in request.form:
            raise Exception("new_rate parametr is required")

        if not request.form["new_rate"]:
            raise Exception("new_rate must be not empty")

        try:
            new_rate = float(request.form["new_rate"])
        except ValueError:
            raise Exception("new_rate must be a number")

        if new_rate <= 0:
            raise Exception("new_rate must be positive")

        updated = (XRate.update(
            {XRate.rate: new_rate, XRate.updated: datetime.datetime.now()})
            .where(XRate.from_currency == from_currency, XRate.to_currency == to_currency).execute()
                   )

        if not updated:
            raise Exception(f"Rate {from_currency} => {to_currency} not found")

        return redirect(url_for('view_rates'))
