import json
import pathlib
import pytest
from .views import index, display

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


def test_vkurse_rate(mocked):
    mocked_response = mocked("vkurse_response.json")
    responses.get(
        "http://vkurse.dp.ua/course.json",
        json=mocked_response,
    )
    e = VkurseExchange("vkurse", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 37.1


def test_nbu_rate(mocked):
    mocked_response = mocked("nbu_response.json")
    responses.get(
        "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json",
        json=mocked_response,
    )
    e = NBUExchange("nbu", "USD", "UAH")
    e.get_rate()
    assert e.pair.sell == 36.5686


def test_currencyapi_rate(mocked):
    mocked_response = mocked("currencyapi_response.json")
    responses.get(
        "https://currencyapi.net/api/v1/rates?base=USD&key=3c9b2a0c-7a3f-11eb-8b1b-7d4d8a7e0b7f",
        json=mocked_response,
    )
    e = CurrencyAPIExchange("currencyapi", "UAH", "USD")
    e.get_rate()
    assert e.pair.sell == 36.912196


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "db_init.yaml")


# @freeze_time("2022-01-01")
@pytest.mark.django_db
def test_index_view():
    response = index(None)
    assert response.status_code == 200
