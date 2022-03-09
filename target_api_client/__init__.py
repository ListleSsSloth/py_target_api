import logging
from typing import Callable, Union

import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient, InvalidGrantError


class TargetApiError(Exception):
    def __init__(self, message, http_status=500):
        self.message = message
        self.http_status = http_status

    def __str__(self):
        return "{} (http status {})".format(self.message, self.http_status)


class TargetValidationError(TargetApiError):
    def __init__(self, fields):
        self.http_status = 400
        self.fields = fields

    def __str__(self):
        return "Validation failed on:\n {}".format(
            "\n  ".join(
                "#{}: {}".format(f, e) for f, e in self.fields.items()
            )
        )


class TargetAuthError(TargetApiError):
    def __init__(self, message, oauth_message):
        self.message = message
        self.oauth_message = oauth_message
        self.http_status = 401

    def __str__(self):
        return "{} (http status {}) {}".format(
            self.message,
            self.http_status,
            self.oauth_message,
        )


class TargetApiClient(object):
    # PRODUCTION_HOST = 'target.my.com'
    # SANDBOX_HOST = 'target-sandbox.my.com'

    # OAUTH_TOKEN_URL = 'v2/oauth2/token.json'
    # OAUTH_USER_URL = '/oauth2/authorize'
    # GRANT_CLIENT = 'client_credentials'
    # GRANT_AGENCY_CLIENT = 'agency_client_credentials'
    # GRANT_RERFESH = 'refresh_token'
    # GRANT_AUTH_CODE = 'authorization_code'
    # OAUTH_ADS_SCOPES = ('read_ads', 'read_payments', 'create_ads')
    # OAUTH_AGENCY_SCOPES = (
    #     'create_clients', 'read_clients', 'create_agency_payments'
    # )
    # OAUTH_MANAGER_SCOPES = (
    #     'read_manager_clients', 'edit_manager_clients', 'read_payments'
    # )
    base_url_default = ""

    def __init__(
        self,
        client_id: str,
        client_secret: str = None,
        token: str = None,
        scopes: tuple = (),
        token_updater: Callable[[dict], None] = None,
        timeout: int = 600,
        base_url: str = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = token
        self._scopes = scopes
        self._base_url = base_url
        self._token_updater_clb = token_updater
        self._timeout = timeout

        # Logging setup
        self.logger = logging.getLogger(__name__)

        # Setup
        self._session = OAuth2Session(
            client=LegacyApplicationClient(
                client_id=self._client_id, scopes=self._scopes
            ),
            auto_refresh_url=self.url_token,
            auto_refresh_kwargs={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            token_updater=self._token_updater,
            token=self._token
        )

    @property
    def url_token(self) -> str:
        return f"{self._base_url}/api/v2/oauth2/token.json"

    def _token_updater(self, token: dict) -> None:
        self._token = token
        if self._token_updater_clb is not None:
            self._token_updater_clb(token)

    def _url_create(self, rpath: str) -> str:
        return f"{self._base_url}/api/{rpath}"

    def _request_data(
        self,
        *args,
        **kwargs
    ) -> Union[str, bool]:
        response = self._request(*args, **kwargs)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204:
            return True
        self._process_error(response)

    def _request(
        self,
        method: str,
        rpath: str,
        check_status: bool = False,
        **kwargs
    ) -> requests.Response:
        url = self._url_create(rpath)
        response = self._session.request(
            method, url, timeout=self._timeout, **kwargs)

        # Check http error
        if check_status and not response.ok:
            raise TargetApiError(f"HTTP Error. Body: {response.text}")
        return response

    def get_ok_lead(self, form_id: str) -> Union[str, bool]:
        """
        Args:
            limit - Количество возвращаемых в ответе лидов. Значение по умолчанию: 20. Максимальное значение: 50.
            offset - Смещение точки отсчета относительно начала списка лидов. Значение по умолчанию: 0.
            _created_time__lt - Лиды, созданные до указанной даты. Дата задается в формате «YYYY-MM-DD hh:mm:ss».
            _created_time__gt - Лиды, созданные после указанной даты. Дата задается в формате «YYYY-MM-DD hh:mm:ss».
            _created_time__lte - Лиды, созданные в указанную дату или до нее. Дата задается в формате «YYYY-MM-DD hh:mm:ss».
            _created_time__gte - Лиды, созданные в указанную дату или после нее. Дата задается в формате «YYYY-MM-DD hh:mm:ss».
            _campaign_id__in - Список идентификаторов кампаний, для которых нужно получить лиды. Идентификаторы задаются в формате «id_1,id_2,…,id_N».
            _campaign_id - Идентификатор кампании, для которой нужно получить лиды. Идентификатор задается в формате «id_1».
            _banner_id__in - Список идентификаторов баннеров, для которых нужно получить лиды. Идентификаторы задаются в формате «id_1,id_2,…,id_N».
            _banner_id - Идентификатор баннера, для которого нужно получить лиды. Идентификатор задается в формате «id_1».
        """  # noqa
        resp = self._request_data(
            rpath="v2/ok/lead_ads/{}.json".format(form_id),
            method="get"
        )
        return resp

    def _process_error(self, resp) -> None:
        body = resp.json()
        if resp.status_code == 400:
            raise TargetValidationError(body)
        if resp.status_code == 401:
            raise TargetAuthError(body, resp.headers.get('WWW-Authenticate'))
        raise TargetApiError(body, resp.status_code)
