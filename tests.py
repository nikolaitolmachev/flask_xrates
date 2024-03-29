import unittest, json, requests, models, api, xmltodict
from unittest.mock import patch
import xml.etree.ElementTree as ET
import api.test_api as test_api

def get_nbrbby_response(*args, **kwds):
    print("get_nbrbby_response")

    class Response:
        def __init__(self, response):
            self.text = json.dumps(response)

        def json(self):
            return json.loads(self.text)

    return Response({"Cur_ID":431,"Date":"2024-02-29T00:00:00","Cur_Abbreviation":"USD","Cur_Scale":1,"Cur_Name":"USD","Cur_OfficialRate":1.1})


class Test(unittest.TestCase):
    def setUp(self):
        models.init_db()


    @unittest.skip("skip")
    def test_main(self):
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        test_api.update_xrates(840, 933)
        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 1.0)
        self.assertGreater(updated_after, updated_before)


    @unittest.skip("skip")
    def test_nbrbby(self):
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        api.update_rate(from_currency=840, to_currency=933)
        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated
        self.assertGreater(xrate.rate, 3.0)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, f'https://api.nbrb.by/exrates/rates/{xrate.from_currency}?parammode=1')
        self.assertIsNotNone(api_log.response_text)


    @unittest.skip("skip")
    def test_belapbby(self):
        xrate = models.XRate.get(from_currency=840, to_currency=933)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)
        api.update_rate(978, 933)

        xrate = models.XRate.get(from_currency=978, to_currency=933)
        updated_after = xrate.updated
        self.assertGreater(xrate.rate, 3.0)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        current_day_str = str(models.peewee_datetime.datetime.now().month) + '/' + str(
            models.peewee_datetime.datetime.now().day) + '/' + \
                          str(models.peewee_datetime.datetime.now().year)
        self.assertEqual(api_log.request_url, f'https://belapb.by/CashConvRatesDaily.php?ondate={current_day_str}')
        self.assertIsNotNone(api_log.response_text)


    @unittest.skip("skip")
    @patch('api._Api._send', new=get_nbrbby_response)
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
        self.assertEqual(api_log.request_url, f'https://api.nbrb.by/exrates/rates/{xrate.from_currency}?parammode=1')
        self.assertIsNotNone(api_log.response_text)

        self.assertEqual('{"Cur_ID": 431, "Date": "2024-02-29T00:00:00", "Cur_Abbreviation": "USD", "Cur_Scale": 1, "Cur_Name": "USD", "Cur_OfficialRate": 1.1}', api_log.response_text)


    @unittest.skip("skip")
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
        self.assertEqual(api_log.request_url, "https://bitpay.com/api/rates")
        self.assertIsNotNone(api_log.response_text)


    def test_xml_api(self):
        r = requests.get("http://localhost:5000/api/xrates/xml")
        self.assertIn("<xrates>", r.text)
        print(r.text)
        xml_rates = xmltodict.parse(r.text)
        self.assertIn("xrates", xml_rates)
        self.assertIsInstance(xml_rates["xrates"]["xrate"], list)
        self.assertEqual(len(xml_rates["xrates"]["xrate"]), 5)


    def test_json_api(self):
        r = requests.get("http://localhost:5000/api/xrates/json")
        json_rates = r.json()
        self.assertIsInstance(json_rates, list)
        self.assertEqual(len(json_rates), 5)
        for rate in json_rates:
            self.assertIn("from", rate)
            self.assertIn("to", rate)
            self.assertIn("rate", rate)


    def test_json_api_byn(self):
        r = requests.get("http://localhost:5000/api/xrates/json?to_currency=933")
        json_rates = r.json()
        self.assertIsInstance(json_rates, list)
        self.assertEqual(len(json_rates), 3)


    def test_html_xrates(self):
        r = requests.get("http://localhost:5000/xrates")
        self.assertTrue(r.ok)
        self.assertIn('<table border="1">', r.text)
        root = ET.fromstring(r.text)
        body = root.find("body")
        self.assertIsNotNone(body)
        table = body.find("table")
        self.assertIsNotNone(table)
        rows = table.findall("tr")
        self.assertEqual(len(rows), 5)

if __name__ == '__main__':
    unittest.main()


