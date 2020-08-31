import logging
from urllib3.util.retry import Retry

import requests
from requests.adapters import HTTPAdapter

logger = logging.getLogger()


class SessionWErrHandling(requests.Session):
    """
    Session that returns response if only "good" status code was returned.
    """
    def general_request(self, url, **kwargs):
        """
        Abstraction to handle GET and POST exceptions.
        :param url: Requested url.
        :param kwargs: Request kwargs with req_type arg to indicate right method.
        """
        typ = kwargs.pop('req_type')
        method = {'GET': super().get, 'POST': super().post}[typ]

        try:
            response = method(url, **kwargs)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            logger.error(f'{typ} request to {url} led to {err}')
        else:
            return response

    def get(self, url, **kwargs):
        kwargs['req_type'] = 'GET'
        return self.general_request(url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        kwargs['req_type'] = 'POST'
        return self.general_request(url, data=data, json=json, **kwargs)


def get_retry_session(
    retries=3,
    backoff_factor=2,
    redirect=30,
    session=None
):
    if not session:
        session = SessionWErrHandling()

    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        redirect=redirect
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
