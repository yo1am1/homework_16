import json
import pathlib
import pytest
from .views import index, vkurse, currencyapi, nbu, privat, monobank

from freezegun import freeze_time

from django.core.management import call_command
import responses

from .exchange_provider import (
    MonoExchange,
    PrivatExchange,
    VkurseExchange,
    NBUExchange,
    CurrencyAPIExchange,
)

root = pathlib.Path(__file__).parent


# Create your tests here.


@pytest.fixture
def mocked():
    def inner(file_name):
        return json.load(open(root / "fixtures" / file_name))

    return inner


@responses.activate
def test_exchange_mono(mocked):
    mocked_response = mocked("mono_response.json")
    responses.get(
        "https://api.monobank.ua/bank/currency",
        json=mocked_response,
    )
    e = MonoExchange("mono", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.4406


@responses.activate
def test_privat_rate(mocked):
    mocked_response = mocked("privat_response.json")
    responses.get(
        "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11",
        json=mocked_response,
    )
    e = PrivatExchange("privat", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.45318


@responses.activate
def test_vkurse_rate(mocked):
    mocked_response = mocked("vkurse_response.json")
    responses.get(
        "http://vkurse.dp.ua/course.json",
        json=mocked_response,
    )
    e = VkurseExchange("vkurse", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.4


@responses.activate
def test_nbu_rate(mocked):
    mocked_response = mocked("nbu_response.json")
    responses.get(
        "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json",
        json=mocked_response,
    )
    e = NBUExchange("nbu", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 36.5686


@responses.activate
def test_currencyapi_rate(mocked):
    mocked_response = mocked("currencyapi_response.json")
    responses.get(
        "https://api.currencyapi.com/v3/latest?apikey=YQeLH52G55DlV361wbi6Vs1cDj3Jg0TG2KTSBIG6&currencies=EUR%2CUSD%2CCAD%2CUAH",
        json=mocked_response,
    )
    e = CurrencyAPIExchange("currencyapi", "UAH", "USD")
    e.get_rate()
    assert e.pair.sell == 36.943381


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "db_init.yaml")


@freeze_time("2023-01-01")
@pytest.mark.django_db
def test_index_view():
    response = index(None)
    assert response.status_code == 200
    assert json.loads(response.content) == {
        "current_rates": [
            {
                "buy": 1.2,
                "currency_a": "USD",
                "currency_b": "EUR",
                "date": "2023-01-01",
                "id": 1,
                "sell": 1.1,
                "vendor": "mono",
            },
            {
                "buy": 1.0,
                "currency_a": "USD",
                "currency_b": "EUR",
                "date": "2023-01-01",
                "id": 2,
                "sell": 1.01,
                "vendor": "privat",
            },
        ]
    }


# region connection tests
def test_privat_view():
    response = privat(None)
    assert response.status_code == 200


def test_vkurse_view():
    response = vkurse(None)
    assert response.status_code == 200


def test_nbu_view():
    response = nbu(None)
    assert response.status_code == 200


def test_currencyapi_view():
    response = currencyapi(None)
    assert response.status_code == 200


def test_monobank_view():
    response = monobank(None)
    assert response.status_code == 200


# endregion
