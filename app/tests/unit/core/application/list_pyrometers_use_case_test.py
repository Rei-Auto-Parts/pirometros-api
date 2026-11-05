from unittest.mock import Mock

from pytest_mock import MockerFixture

from core.application.list_pyrometers_use_case import ListPyrometersUseCase
from core.domain.dtos.pyrometer_dto import PyrometerDto
from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto
from core.domain.models.default_color_model import assign_default_colors
from interfaces.adapters.repositories.i_pyrometer_profile_repository import (
    IPyrometerProfileRepository,
)
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository

PI12 = "C24C.F90D.0000"
PI14 = "B68A.1010.0000"


def build_use_case(
    mocker: MockerFixture, pyrometers: list[PyrometerDto], profiles: list[PyrometerProfileDto]
) -> tuple[ListPyrometersUseCase, Mock, Mock]:
    readings = mocker.Mock(spec=IReadingRepository)
    readings.find_pyrometers.return_value = pyrometers
    profile_repository = mocker.Mock(spec=IPyrometerProfileRepository)
    profile_repository.find_all.return_value = profiles
    return ListPyrometersUseCase(readings, profile_repository), readings, profile_repository


def test_should_apply_defaults_when_pyrometer_has_no_profile(mocker: MockerFixture) -> None:
    # Arrange
    use_case, _, _ = build_use_case(mocker, [PyrometerDto(PI12, "PI-12")], [])

    # Act
    result = use_case.execute()

    # Assert
    assert len(result) == 1
    item = result[0]
    assert (item.id, item.name, item.nickname, item.note, item.active) == (
        PI12,
        "PI-12",
        None,
        None,
        True,
    )
    assert item.color == assign_default_colors([PI12])[PI12]


def test_should_return_the_profile_when_pyrometer_has_one(mocker: MockerFixture) -> None:
    # Arrange
    profile = PyrometerProfileDto(PI12, "Forno 2", "#e11d48", "termopar trocado", False)
    use_case, _, _ = build_use_case(mocker, [PyrometerDto(PI12, "PI-12")], [profile])

    # Act
    item = use_case.execute()[0]

    # Assert
    assert (item.nickname, item.color, item.note, item.active) == (
        "Forno 2",
        "#e11d48",
        "termopar trocado",
        False,
    )


def test_should_use_default_color_when_profile_has_no_color(mocker: MockerFixture) -> None:
    # Arrange
    profile = PyrometerProfileDto(PI12, "Forno 2", None, None, True)
    use_case, _, _ = build_use_case(mocker, [PyrometerDto(PI12, "PI-12")], [profile])

    # Act
    item = use_case.execute()[0]

    # Assert
    assert item.color == assign_default_colors([PI12])[PI12]


def test_should_order_by_serial_when_listing(mocker: MockerFixture) -> None:
    # Arrange
    pyrometers = [PyrometerDto(PI12, "PI-12"), PyrometerDto(PI14, "PI-14")]
    use_case, _, _ = build_use_case(mocker, pyrometers, [])

    # Act
    result = use_case.execute()

    # Assert
    assert [item.id for item in result] == [PI14, PI12]


def test_should_pick_different_default_colors_when_pyrometers_have_no_color(
    mocker: MockerFixture,
) -> None:
    # Arrange
    pyrometers = [PyrometerDto(PI12, "PI-12"), PyrometerDto(PI14, "PI-14")]
    use_case, _, _ = build_use_case(mocker, pyrometers, [])

    # Act
    colors = {item.color for item in use_case.execute()}

    # Assert
    assert len(colors) == 2


def test_should_query_each_repository_once_when_executed(mocker: MockerFixture) -> None:
    # Arrange
    use_case, readings, profile_repository = build_use_case(mocker, [], [])

    # Act
    use_case.execute()

    # Assert
    readings.find_pyrometers.assert_called_once_with()
    profile_repository.find_all.assert_called_once_with()
