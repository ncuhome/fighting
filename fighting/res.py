import requests


class ResError(Exception):
    """ResException"""


class Res(object):
    """Fighting client"""

    def __init__(self, url_prefix=''):
        self.url_prefix = url_prefix

    def post(self, url, data=None):
        """Send request to Fighting server"""
        url = self.url_prefix + url
        try:
            response = requests.post(url, json=data)
        except requests.RequestException as ex:
            raise ResError(str(ex)) from None
        try:
            response.raise_for_status()
        except requests.HTTPError as ex:
            try:
                msg = response.json()
            except ValueError:
                msg = str(ex)
            raise ResError(msg) from None
        try:
            return response.json()
        except ValueError:
            raise ResError("response data not valid JSON document") from None
