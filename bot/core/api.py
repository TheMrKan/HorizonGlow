from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
import datetime
import httpx
import logging
from typing import Self

logger = logging.getLogger(__name__)


class ProductInfo(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    description: str
    category: int
    number: str
    score: str
    produced_at: datetime.datetime
    price: float
    support_code: str
    is_support_period_expired: bool
    purchased_at: datetime.datetime | None
    purchased_by: int | None


class APIClient:
    instance: Self

    base_url: str
    client: httpx.AsyncClient
    username: str
    password: str
    secret_phrase: str
    headers: dict

    class AuthError(Exception):
        pass

    def __init__(self, base_url: str, username: str, password: str, secret_phrase: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.username = username
        self.password = password
        self.secret_phrase = secret_phrase

    async def authenticate_async(self):
        data = {"username": self.username, "password": self.password, "secretPhrase": self.secret_phrase}
        response = await self.client.post(self.base_url + "auth/login/", data=data)
        self.raise_auth_errors(response)

    def raise_auth_errors(self, response: httpx.Response):
        if response.status_code == 403 or response.status_code == 401:
            raise self.AuthError

    @staticmethod
    def auto_auth(method):
        async def wrapper(self, *args, **kwargs):
            try:
                return await method(self, *args, **kwargs)
            except self.AuthError:
                logger.info("Authentication was not provided or outdated. Renewing...")
                await self.authenticate_async()
                logger.info("Authentication updated, retrying...")
                return await method(self, *args, **kwargs)
        return wrapper

    @auto_auth
    async def fetch_product_by_support_code_async(self, support_code: str) -> ProductInfo | None:
        response = await self.client.get(self.base_url + f"products/?support_code={support_code}")
        self.raise_auth_errors(response)

        result = response.json()
        if not any(result):
            return None

        product_info = ProductInfo(**result[0])
        return product_info
