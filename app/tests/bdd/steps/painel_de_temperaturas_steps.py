from datetime import datetime
from typing import Any

from behave import given, then, when

from tests.support.receiver_data_fixture import (
    insert_generated,
    insert_reading,
    snapshot_readings,
)

DEVICES = {"PI-12": "C24C.F90D.0000", "PI-14": "B68A.1010.0000"}
DAY = datetime(2026, 10, 29, 0, 0, 0)
READING_FIELDS = {
    "id",
    "gateway_id",
    "gateway_name",
    "pyrometer_id",
    "pyrometer_name",
    "measured_at",
    "thermocouple",
    "unit",
    "cold_junction",
    "read_delay",
    "place",
    "battery",
    "temperature",
    "detect_time",
}


def period_of_day(day: str) -> dict[str, str]:
    """`dd/MM/yyyy` para o periodo do dia inteiro."""
    parsed = datetime.strptime(day, "%d/%m/%Y")
    return {
        "start": parsed.strftime("%Y-%m-%dT00:00:00"),
        "end": parsed.strftime("%Y-%m-%dT23:59:59"),
    }


def seed(context: Any, reading_id: int, measured_at: datetime, device: str) -> None:
    insert_reading(context.engine, reading_id, measured_at, DEVICES[device], device)


def measured_at_of(response: Any) -> list[str]:
    return [item["measured_at"] for item in response.json()["items"]]


@given("que toda consulta de leituras ou de série informa um período, com início e fim")
def period_is_always_informed(context: Any) -> None:
    context.period = {"start": "2026-10-01T00:00:00", "end": "2026-10-31T23:59:59"}


@given('que existem leituras dos pirômetros "{first}" e "{second}" no dia 29/10/2026')
def readings_of_two_pyrometers_on_day(context: Any, first: str, second: str) -> None:
    seed(context, 1, datetime(2026, 10, 29, 10, 0, 0), first)
    seed(context, 2, datetime(2026, 10, 29, 11, 0, 0), second)
    seed(context, 3, datetime(2026, 10, 29, 12, 0, 0), first)


@given('que o "{device}" mediu às 09:00 e essa leitura foi gravada depois de uma das 14:02')
def late_delivery(context: Any, device: str) -> None:
    seed(context, 1, datetime(2026, 10, 29, 14, 2, 0), device)
    seed(context, 2, datetime(2026, 10, 29, 9, 0, 0), device)


@given('que existem leituras de "{first}" e "{second}" no mesmo período')
def readings_in_same_period(context: Any, first: str, second: str) -> None:
    seed(context, 1, datetime(2026, 10, 29, 10, 0, 0), first)
    seed(context, 2, datetime(2026, 10, 29, 11, 0, 0), second)


@given("que existem leituras em 28/10/2026 e em 29/10/2026")
def readings_on_two_days(context: Any) -> None:
    seed(context, 1, datetime(2026, 10, 28, 10, 0, 0), "PI-12")
    seed(context, 2, datetime(2026, 10, 29, 10, 0, 0), "PI-12")


@given("que existem mais de 500 leituras no período")
def more_than_500_readings(context: Any) -> None:
    insert_generated(context.engine, 600, DAY)


@given("uma leitura gravada em 2026-10-29 11:00:30")
def single_reading(context: Any) -> None:
    seed(context, 1, datetime(2026, 10, 29, 11, 0, 30), "PI-12")


@given('leituras de "{first}" e "{second}" no dia 29/10/2026')
def readings_for_series(context: Any, first: str, second: str) -> None:
    seed(context, 1, datetime(2026, 10, 29, 11, 0, 0), first)
    seed(context, 2, datetime(2026, 10, 29, 9, 0, 0), second)
    seed(context, 3, datetime(2026, 10, 29, 10, 0, 0), first)


@given('que existem leituras de "{first}" e "{second}"')
def readings_of_two_pyrometers(context: Any, first: str, second: str) -> None:
    seed(context, 1, datetime(2026, 10, 29, 10, 0, 0), first)
    seed(context, 2, datetime(2026, 10, 29, 11, 0, 0), second)


@when("eu consulto as leituras desse dia")
def list_readings_of_day(context: Any) -> None:
    context.response = context.client.get("/api/readings", params=period_of_day("29/10/2026"))


@when('eu consulto as leituras do "{device}" nesse período')
def list_readings_of_pyrometer(context: Any, device: str) -> None:
    context.response = context.client.get(
        "/api/readings", params={**context.period, "dev_id": DEVICES[device]}
    )


@when("eu consulto as leituras de {day}")
def list_readings_of_given_day(context: Any, day: str) -> None:
    context.response = context.client.get("/api/readings", params=period_of_day(day))


@when("eu consulto as leituras sem informar o tamanho da página")
def list_readings_with_default_page(context: Any) -> None:
    context.response = context.client.get("/api/readings", params=period_of_day("29/10/2026"))


@when("eu consulto as leituras")
def list_readings(context: Any) -> None:
    context.response = context.client.get("/api/readings", params=context.period)


@when("eu consulto a série desse dia")
def get_series_of_day(context: Any) -> None:
    context.response = context.client.get(
        "/api/readings/series", params=period_of_day("29/10/2026")
    )


@when("eu consulto a série de um período de 40 dias")
def get_series_of_forty_days(context: Any) -> None:
    context.response = context.client.get(
        "/api/readings/series",
        params={"start": "2026-10-01T00:00:00", "end": "2026-11-10T00:00:00"},
    )


@when("eu consulto os pirômetros")
def list_pyrometers(context: Any) -> None:
    context.response = context.client.get("/api/pyrometers")


@when("eu consulto as leituras, a série e os pirômetros")
def query_everything(context: Any) -> None:
    context.before = snapshot_readings(context.engine)
    context.client.get("/api/readings", params=context.period)
    context.client.get("/api/readings/series", params=context.period)
    context.client.get("/api/pyrometers")


@then("recebo as leituras da mais recente para a mais antiga pela data da medição")
def readings_are_newest_first(context: Any) -> None:
    dates = measured_at_of(context.response)
    assert dates == sorted(dates, reverse=True)
    assert len(dates) == 3


@then("cada leitura traz todos os dados da medição gravados")
def readings_have_every_field(context: Any) -> None:
    for item in context.response.json()["items"]:
        assert set(item) == READING_FIELDS


@then("a leitura das 09:00 vem depois da leitura das 14:02")
def late_reading_comes_after(context: Any) -> None:
    dates = measured_at_of(context.response)
    assert dates.index("2026-10-29T09:00:00") > dates.index("2026-10-29T14:02:00")


@then('recebo somente leituras do "{device}"')
def only_readings_of_pyrometer(context: Any, device: str) -> None:
    items = context.response.json()["items"]
    assert items
    assert {item["pyrometer_name"] for item in items} == {device}


@then("recebo somente leituras de 29/10/2026")
def only_readings_of_day(context: Any) -> None:
    dates = measured_at_of(context.response)
    assert dates
    assert all(date.startswith("2026-10-29") for date in dates)


@then("recebo {count:d} leituras")
def receive_count_of_readings(context: Any, count: int) -> None:
    assert len(context.response.json()["items"]) == count


@then("se eu pedir mais de 500 por página, recebo um erro de validação")
def page_size_above_limit_is_rejected(context: Any) -> None:
    response = context.client.get(
        "/api/readings", params={**period_of_day("29/10/2026"), "page_size": 501}
    )
    assert response.status_code == 422


@then('a data devolvida é "{expected}" sem offset de fuso')
def date_has_no_offset(context: Any, expected: str) -> None:
    assert measured_at_of(context.response) == [expected]


@then("recebo uma série para cada pirômetro, ordenada pela data da medição")
def series_per_pyrometer(context: Any) -> None:
    series = context.response.json()
    assert {item["pyrometer_name"] for item in series} == {"PI-12", "PI-14"}
    for item in series:
        dates = [point["measured_at"] for point in item["points"]]
        assert dates == sorted(dates)


@then("recebo um erro de validação informando o máximo de 31 dias")
def period_too_long(context: Any) -> None:
    assert context.response.status_code == 422
    assert "31" in context.response.json()["detail"]


@then("recebo os dois, cada um com serial e nome")
def both_pyrometers_with_serial_and_name(context: Any) -> None:
    assert context.response.json() == [
        {"id": DEVICES["PI-14"], "name": "PI-14"},
        {"id": DEVICES["PI-12"], "name": "PI-12"},
    ]


@then("a tabela de leituras permanece idêntica")
def table_is_unchanged(context: Any) -> None:
    assert snapshot_readings(context.engine) == context.before
