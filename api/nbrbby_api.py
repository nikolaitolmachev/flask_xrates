from api import _Api
from config import CODE_CURRENCY


class Api(_Api):
    def __init__(self):
        super().__init__('NBRBbyApi')

    def _update_rate(self, xrate):
        rate = self._get_NBRBby_rate(xrate.from_currency)
        return rate

    def _get_NBRBby_rate(self, from_currency):
        if from_currency not in CODE_CURRENCY:
            raise ValueError(f'Invalid from_currency: {from_currency}')
        response = self._send_request(f'https://api.nbrb.by/exrates/rates/{from_currency}?parammode=1', method='get')
        json_format = response.json()
        self.log.debug('nbrb.by response: %s' % json_format)

        try:
            rate = float(json_format['Cur_OfficialRate'])
        except ValueError:
            raise ValueError(f'Invalid NBRB.by response: {CODE_CURRENCY[from_currency]} not found')

        return rate