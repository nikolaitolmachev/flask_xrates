import json
import unittest
from html.parser import HTMLParser
from unittest.mock import patch

import xmltodict

from app import create_app
from app import models
from app import api
from app.api.nbrbby_api import URL as URL_BY
from app.api.crypto_api import URL as URL_CRYPTO


def get_nbrbby_response(*_args, **_kwargs):
    print("get_nbrbby_response")

    class Response:
        def __init__(self, response):
            self.text = json.dumps(response)

        def json(self):
            return json.loads(self.text)

    return Response({
        "Cur_ID": 431,
        "Date": "2024-02-29T00:00:00",
        "Cur_Abbreviation": "USD",
        "Cur_Scale": 1,
        "Cur_Name": "USD",
        "Cur_OfficialRate": 1.1
    })


class Test(unittest.TestCase):
    app = None
    client = None

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        models.init_db()

    def test_nbrbby(self):
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        api.update_rate(from_currency=840, to_currency=933)
        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated
        self.assertNotEqual(xrate.rate, 1.0)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        self.assertEqual(
            api_log.request_url,
            URL_BY.format(from_currency=xrate.from_currency),
        )
        self.assertIsNotNone(api_log.response_text)

    @patch('app.api._Api._send', new=get_nbrbby_response)
    def test_nbrbby_mock(self):
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        api.update_rate(840, 933)
        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated
        self.assertEqual(xrate.rate, 1.1)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        self.assertEqual(
            api_log.request_url,
            URL_BY.format(from_currency=xrate.from_currency),
        )
        self.assertIsNotNone(api_log.response_text)
        self.assertEqual(
            api_log.response_text,
            '{"Cur_ID": 431, "Date": "2024-02-29T00:00:00", "Cur_Abbreviation": "USD", "Cur_Scale": 1, '
            '"Cur_Name": "USD", "Cur_OfficialRate": 1.1}'
        )

    def test_crypto_byn(self):
        xrate = models.XRate.get(from_currency=1000, to_currency=933)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        api.update_rate(from_currency=1000, to_currency=933)

        xrate = models.XRate.get(from_currency=1000, to_currency=933)
        updated_after = xrate.updated
        self.assertGreater(xrate.rate, 150000)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, URL_CRYPTO)
        self.assertIsNotNone(api_log.response_text)

    def test_root_shows_rates(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('<table', r.data.decode())

    def test_xml_api(self):
        r = self.client.get('/api/xrates/xml')
        self.assertEqual(r.status_code, 200)
        self.assertIn("<xrates>", r.text)
        xml_rates = xmltodict.parse(r.text)
        self.assertIn("xrates", xml_rates)
        self.assertIsInstance(xml_rates["xrates"]["xrate"], list)
        self.assertGreater(len(xml_rates["xrates"]["xrate"]), 0)

    def test_json_api(self):
        r = self.client.get('/api/xrates/json')
        self.assertEqual(r.status_code, 200)
        json_rates = r.json
        self.assertIsInstance(json_rates, list)
        self.assertGreater(len(json_rates), 0)
        for rate in json_rates:
            self.assertIn("from", rate)
            self.assertIn("to", rate)
            self.assertIn("rate", rate)

    def test_json_api_filter(self):
        r = self.client.get('/api/xrates/json?to_currency=933')
        self.assertEqual(r.status_code, 200)
        json_rates = r.json
        self.assertIsInstance(json_rates, list)
        self.assertGreater(len(json_rates), 0)
        for rate in json_rates:
            self.assertEqual(rate["to"], 933)

    def test_html_xrates(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        html = r.data.decode()
        self.assertIn('<table', html)

        parser = _TableParser()
        parser.feed(html)
        self.assertGreater(len(parser.rows), 0)


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self._current_row = None
        self._in_td = False

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self._current_row = []
        elif tag == 'td' and self._current_row is not None:
            self._in_td = True

    def handle_endtag(self, tag):
        if tag == 'tr' and self._current_row is not None:
            self.rows.append(self._current_row)
            self._current_row = None
        elif tag == 'td':
            self._in_td = False

    def handle_data(self, data):
        if self._in_td and self._current_row is not None:
            self._current_row.append(data.strip())


if __name__ == '__main__':
    unittest.main()
