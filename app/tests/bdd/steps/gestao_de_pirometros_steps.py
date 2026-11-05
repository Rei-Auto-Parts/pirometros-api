from datetime import datetime
from typing import Any

from behave import given, then, when
from sqlalchemy import text

from tests.support.receiver_data_fixture import insert_reading, snapshot_readings

DEVICES = {"PI-12": "C24C.F90D.0000", "PI-14": "B68A.1010.0000"}
UNKNOWN_SERIAL = "ZZZZ.0000.0000"
PERIOD = {"start": "2026-11-05T00:00:00", "end": "2026-11-05T23:59:59"}


def at(clock_text: str) -> datetime:
    return datetime.strptime(f"2026-11-05 {clock_text}", "%Y-%m-%d %H:%M:%S")


def serial_of(name: str) -> str:
    return DEVICES[name]


def put_profile(context: Any, name: str, **fields: Any) -> Any:
    return context.client.put(f"/api/pyrometers/{serial_of(name)}", json=fields)


def listed(context: Any, name: str) -> dict[str, Any]:
    items = context.client.get("/api/pyrometers").json()
    return next(item for item in items if item["id"] == serial_of(name))


def summary_of(context: Any, name: str) -> dict[str, Any]:
    items = context.client.get("/api/pyrometers/summary").json()
    return next(item for item in items if item["pyrometer_id"] == serial_of(name))


@given('que existem leituras do pirômetro "{name}" e nenhum complemento gravado')
def pyrometer_with_readings_and_no_profile(context: Any, name: str) -> None:
    insert_reading(context.engine, 1, at("10:00:00"), serial_of(name), name)
    context.pyrometer = name


@given('que "{name}" tem o apelido "{nickname}"')
def pyrometer_with_nickname(context: Any, name: str, nickname: str) -> None:
    insert_reading(context.engine, 1, at("10:00:00"), serial_of(name), name)
    put_profile(context, name, nickname=nickname)
    context.pyrometer = name


@given('que "{name}" tem a cor "{color}" e que "{other}" existe')
def pyrometer_with_color_and_another(context: Any, name: str, color: str, other: str) -> None:
    insert_reading(context.engine, 1, at("10:00:00"), serial_of(name), name)
    insert_reading(context.engine, 2, at("10:00:00"), serial_of(other), other)
    put_profile(context, name, color=color)


@given('que "{name}" tem a cor "{color}"')
def pyrometer_with_color(context: Any, name: str, color: str) -> None:
    insert_reading(context.engine, 1, at("10:00:00"), serial_of(name), name)
    put_profile(context, name, color=color)
    context.pyrometer = name


@given('que não existem leituras do serial "{serial}"')
def serial_without_readings(context: Any, serial: str) -> None:
    context.unknown_serial = serial


@given('que "{first}" e "{second}" não têm cor escolhida')
def pyrometers_without_color(context: Any, first: str, second: str) -> None:
    insert_reading(context.engine, 1, at("10:00:00"), serial_of(first), first)
    insert_reading(context.engine, 2, at("10:00:00"), serial_of(second), second)


@given(
    'que "{name}" tem leituras às {first} ({first_temp:d} graus, bateria {first_battery:d}) '
    "e às {second} ({second_temp:d} graus, bateria {second_battery:d})"
)
def two_readings_with_battery(
    context: Any,
    name: str,
    first: str,
    first_temp: int,
    first_battery: int,
    second: str,
    second_temp: int,
    second_battery: int,
) -> None:
    serial = serial_of(name)
    insert_reading(context.engine, 1, at(first), serial, name, first_temp, battery=first_battery)
    insert_reading(context.engine, 2, at(second), serial, name, second_temp, battery=second_battery)


@given("que agora são {clock_text}")
def now_is(context: Any, clock_text: str) -> None:
    context.clock.current = at(clock_text)


@given(
    'que "{name}" tem uma leitura às {first} com {temp:d} graus e a mais recente, às {second}, '
    "sem temperatura"
)
def latest_reading_without_temperature(
    context: Any, name: str, first: str, temp: int, second: str
) -> None:
    serial = serial_of(name)
    insert_reading(context.engine, 1, at(first), serial, name, temp)
    insert_reading(context.engine, 2, at(second), serial, name, None)
    context.clock.current = at("10:08:00")


@given("que existem 3 leituras no período, uma delas sem temperatura")
def three_readings_one_without_temperature(context: Any) -> None:
    insert_reading(context.engine, 1, at("10:00:00"), temperature=1500)
    insert_reading(context.engine, 2, at("11:00:00"), temperature=None)
    insert_reading(context.engine, 3, at("12:00:00"), temperature=1520)


@given('que existem leituras de "{name}" no período, uma sem temperatura')
def readings_one_without_temperature(context: Any, name: str) -> None:
    serial = serial_of(name)
    insert_reading(context.engine, 1, at("10:00:00"), serial, name, 1500)
    insert_reading(context.engine, 2, at("11:00:00"), serial, name, None)
    context.missing_id = 2


@when('eu gravo o apelido "{nickname}", a cor "{color}" e a observação "{note}" para ele')
def save_full_profile(context: Any, nickname: str, color: str, note: str) -> None:
    context.saved = {"nickname": nickname, "color": color, "note": note}
    context.response = put_profile(context, context.pyrometer, **context.saved)


@when('eu gravo o apelido "{nickname}" para ele')
def save_nickname(context: Any, nickname: str) -> None:
    context.response = put_profile(context, context.pyrometer, nickname=nickname)


@when("eu o marco como inativo")
def deactivate(context: Any) -> None:
    context.response = put_profile(context, context.pyrometer, active=False)


@when("eu tento gravar um complemento para ele")
def save_for_unknown_serial(context: Any) -> None:
    context.response = context.client.put(
        f"/api/pyrometers/{context.unknown_serial}", json={"nickname": "Forno"}
    )


@when('eu gravo para "{name}" a cor "{color}"')
def save_color(context: Any, name: str, color: str) -> None:
    context.response = put_profile(context, name, color=color)


@when('eu gravo para "{name}" a cor que "{other}" mostra')
def save_color_shown_by_other(context: Any, name: str, other: str) -> None:
    context.response = put_profile(context, name, color=listed(context, other)["color"])


@when('eu gravo para "{name}" o apelido "{nickname}" e a cor "{color}"')
def save_nickname_and_color(context: Any, name: str, nickname: str, color: str) -> None:
    context.response = put_profile(context, name, color=color, nickname=nickname)


@when('eu gravo para "{name}" um apelido com {size:d} caracteres')
def save_long_nickname(context: Any, name: str, size: int) -> None:
    context.response = put_profile(context, name, nickname="x" * size)


@when("eu consulto os pirômetros duas vezes")
def list_twice(context: Any) -> None:
    context.first_listing = context.client.get("/api/pyrometers").json()
    context.second_listing = context.client.get("/api/pyrometers").json()


@when("eu consulto o resumo")
def get_summary(context: Any) -> None:
    context.response = context.client.get("/api/pyrometers/summary")


@when("eu consulto as leituras do período")
def list_readings_of_period(context: Any) -> None:
    context.response = context.client.get("/api/readings", params=PERIOD)


@when("eu consulto a série do período")
def get_series_of_period(context: Any) -> None:
    context.response = context.client.get("/api/readings/series", params=PERIOD)


@when('chegam novas leituras de "{name}"')
def new_readings_arrive(context: Any, name: str) -> None:
    insert_reading(context.engine, 10, at("11:00:00"), serial_of(name), name)
    insert_reading(context.engine, 11, at("11:05:00"), serial_of(name), name)


@when("eu gravo um complemento e consulto leituras, série, resumo e pirômetros")
def save_and_query_everything(context: Any) -> None:
    context.before = snapshot_readings(context.engine)
    context.client.put(f"/api/pyrometers/{serial_of('PI-12')}", json={"nickname": "Forno 2"})
    context.client.get("/api/readings", params=PERIOD)
    context.client.get("/api/readings/series", params=PERIOD)
    context.client.get("/api/pyrometers/summary")
    context.client.get("/api/pyrometers")


@then('"{name}" vem ativo, sem apelido, sem observação e com uma cor padrão')
def defaults_are_applied(context: Any, name: str) -> None:
    item = listed(context, name)
    assert item["active"] is True
    assert item["nickname"] is None
    assert item["note"] is None
    assert item["color"].startswith("#")


@then('a lista de pirômetros traz "{name}" com esse apelido, essa cor e essa observação')
def profile_is_listed(context: Any, name: str) -> None:
    item = listed(context, name)
    assert (item["nickname"], item["color"], item["note"]) == (
        context.saved["nickname"],
        context.saved["color"],
        context.saved["note"],
    )


@then('a lista traz o apelido "{nickname}"')
def nickname_is_listed(context: Any, nickname: str) -> None:
    assert listed(context, context.pyrometer)["nickname"] == nickname


@then('não existe um segundo complemento para "{name}"')
def only_one_profile(context: Any, name: str) -> None:
    with context.engine.connect() as connection:
        count = connection.execute(
            text("SELECT count(*) FROM app.pyrometer_profile WHERE pyrometer_id = :id"),
            {"id": serial_of(name)},
        ).scalar_one()
    assert count == 1


@then('a lista traz "{name}" como inativo')
def pyrometer_is_inactive(context: Any, name: str) -> None:
    assert listed(context, name)["active"] is False


@then("as leituras dele continuam consultáveis")
def readings_still_available(context: Any) -> None:
    response = context.client.get("/api/readings", params=PERIOD)
    assert response.json()["total"] == 1


@then('recebo um erro de "não encontrado"')
def not_found_error(context: Any) -> None:
    assert context.response.status_code == 404


@then("nada é gravado")
def nothing_is_saved(context: Any) -> None:
    with context.engine.connect() as connection:
        count = connection.execute(text("SELECT count(*) FROM app.pyrometer_profile")).scalar_one()
    assert count == 0


@then("recebo um erro de validação informando o formato de cor aceito")
def color_format_error(context: Any) -> None:
    assert context.response.status_code == 422
    assert "color" in str(context.response.json()["detail"])


@then("o complemento anterior permanece")
def previous_profile_remains(context: Any) -> None:
    assert listed(context, context.pyrometer)["nickname"] == "Forno 2"


@then("recebo um erro de conflito informando que a cor já está em uso")
def color_conflict_error(context: Any) -> None:
    assert context.response.status_code == 409
    assert "ja esta em uso" in context.response.json()["detail"]


@then('nada muda para "{name}"')
def nothing_changes_for(context: Any, name: str) -> None:
    item = listed(context, name)
    assert (item["nickname"], item["note"], item["active"]) == (None, None, True)


@then('a lista traz "{name}" com a cor "{color}" e o apelido "{nickname}"')
def listed_with_color_and_nickname(context: Any, name: str, color: str, nickname: str) -> None:
    item = listed(context, name)
    assert (item["color"], item["nickname"]) == (color, nickname)


@then("recebo um erro de validação informando o máximo de {size:d} caracteres")
def max_length_error(context: Any, size: int) -> None:
    assert context.response.status_code == 422
    assert str(size) in str(context.response.json()["detail"])


@then("a cor de cada um é a mesma nas duas consultas")
def colors_are_stable(context: Any) -> None:
    first = {item["id"]: item["color"] for item in context.first_listing}
    second = {item["id"]: item["color"] for item in context.second_listing}
    assert first == second


@then('"{first}" e "{second}" têm cores diferentes')
def colors_differ(context: Any, first: str, second: str) -> None:
    assert listed(context, first)["color"] != listed(context, second)["color"]


@then(
    '"{name}" traz {temp:d} graus, bateria {battery:d}, a data {clock_text} '
    "e {minutes:d} minutos sem leitura"
)
def summary_with_battery_and_minutes(
    context: Any, name: str, temp: int, battery: int, clock_text: str, minutes: int
) -> None:
    item = summary_of(context, name)
    assert (item["temperature"], item["battery"], item["minutes_without_reading"]) == (
        temp,
        battery,
        minutes,
    )
    assert item["measured_at"] == at(clock_text).isoformat()


@then('"{name}" traz {temp:d} graus e a data {clock_text}')
def summary_with_temperature_and_date(context: Any, name: str, temp: int, clock_text: str) -> None:
    item = summary_of(context, name)
    assert item["temperature"] == temp
    assert item["measured_at"] == at(clock_text).isoformat()


@then("recebo {items:d} itens e o total é {total:d}")
def items_and_total(context: Any, items: int, total: int) -> None:
    body = context.response.json()
    assert (len(body["items"]), body["total"]) == (items, total)


@then('a série de "{name}" não traz o ponto sem temperatura')
def series_has_no_missing_point(context: Any, name: str) -> None:
    series = context.response.json()
    points = [point["id"] for item in series for point in item["points"]]
    assert context.missing_id not in points
    assert len(points) == 1


@then('a lista continua trazendo o apelido "{nickname}"')
def nickname_still_listed(context: Any, nickname: str) -> None:
    assert listed(context, context.pyrometer)["nickname"] == nickname
