import xml.etree.ElementTree as ET
from models import peewee_datetime

from api import _Api
from config import CODE_CURRENCY

class Api(_Api):
    def __init__(self):
        super().__init__('BELAPBbyApi')

    def _update_rate(self, xrate):
        rate = self._get_BELAPBby_rate(xrate.from_currency, xrate.to_currency)
        return rate

    def _get_BELAPBby_rate(self, from_currency, to_currency):
        if isinstance(from_currency, int) and isinstance(to_currency, int):
            from_currency = CODE_CURRENCY.get(from_currency)
            to_currency = CODE_CURRENCY.get(to_currency)

        current_day_str = str(peewee_datetime.datetime.now().month) + '/' + str(
            peewee_datetime.datetime.now().day) + '/' + \
                          str(peewee_datetime.datetime.now().year)

        response = self._send_request(url=f'https://belapb.by/CashConvRatesDaily.php?ondate={current_day_str}', method='get')
        self.log.debug('belapb.by response.encoding: %s' % response.encoding)
        response_text = response.text
        self.log.debug('belapb.by response.text: %s' % response_text)
        rate = self._find_rate(response_text, from_currency, to_currency)

        return rate

    def _find_rate(self, response_text, from_currency, to_currency):
        root = ET.fromstring(response_text)
        currency = root.findall('Currency')

        for curr in currency:
            if curr.find('CurrSrc').text == from_currency and curr.find('CurrTrg').text == to_currency:
                return float(curr.find('ConvRate').text)

        raise ValueError(f'Invalid BELAPB.by response: {from_currency} => {to_currency}  not found')





