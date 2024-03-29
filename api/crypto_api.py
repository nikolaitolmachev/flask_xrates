from api import _Api
from config import CODE_CURRENCY

class Api(_Api):

    def __init__(self):
        super().__init__('CryptoApi')

    def _update_rate(self, xrate):
        rate = self._get_api_rate(xrate.to_currency)
        return rate

    def _get_api_rate(self, to_currency):
        if to_currency not in CODE_CURRENCY:
            raise ValueError(f'Invalid to_currency: {to_currency}')

        URL = 'https://bitpay.com/api/rates'
        response = self._send_request(URL, method='get')
        response_json = response.json()
        self.log.debug('Crypto response got')
        rate = self._find_rate(response_json, to_currency)

        return rate

    def _find_rate(self, response_data, to_currency):
        try:
            for item in response_data:
                if item['code'] == CODE_CURRENCY[to_currency]:
                    return float(item['rate'])
        except KeyError:
            raise ValueError(f'Invalid crypto response.')
