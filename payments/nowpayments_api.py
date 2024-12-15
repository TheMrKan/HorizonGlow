import requests
from dataclasses import dataclass


class APIError(Exception):
    pass


def __get_auth_headers(api_key: str) -> dict:
    return {"x-api-key": api_key}


@dataclass
class CreatedInvoice:
    id: str
    invoice_url: str


def create_invoice(api_key: str,
                   price: float,
                   price_currency: str,
                   pay_currency: str | None = None,
                   callback_url: str | None = None,
                   order_id: str | None = None,
                   success_url: str | None = None,
                   cancel_url: str | None = None,
                   ) -> CreatedInvoice:

    data = {"price_amount": price, "price_currency": price_currency}
    if pay_currency:
        data["pay_currency"] = pay_currency
    if callback_url:
        data["ipn_callback_url"] = callback_url
    if order_id:
        data["order_id"] = order_id
    if success_url:
        data["success_url"] = success_url
    if cancel_url:
        data["cancel_url"] = cancel_url

    response = requests.post(
        url="https://api.nowpayments.io/v1/invoice",
        headers=__get_auth_headers(api_key),
        json=data
    )

    if response.status_code != 200:
        raise APIError(f"Invalid status code {response.status_code}. Response: {response.text}")

    json = response.json()
    return CreatedInvoice(json["id"], json["invoice_url"])
