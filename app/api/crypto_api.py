from . import _Api
from ..config import CODE_CURRENCY


URL = "https://bitpay.com/api/rates"


class Api(_Api):

    def __init__(self):
        super().__init__("CryptoApi")

    def _update_rate(self, xrate):
        rate = self._get_api_rate(xrate.to_currency)
        return rate

    def _get_api_rate(self, to_currency):
        if to_currency not in CODE_CURRENCY:
            raise ValueError(f"Invalid to_currency: {to_currency}")

        response = self._send_request(URL, method="get")
        response_json = response.json()
        self.log.debug("Crypto response got")
        rate = self._find_rate(response_json, to_currency)

        return rate

    @staticmethod
    def _find_rate(response_data, to_currency):
        expected_code = CODE_CURRENCY[to_currency]
        for item in response_data:
            if item.get("code") == expected_code:
                return float(item["rate"])

        raise ValueError(f"Currency {expected_code} not found")
