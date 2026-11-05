from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from core.application.save_pyrometer_profile_use_case import SavePyrometerProfileUseCase
from core.domain.dtos.pyrometer_dto import PyrometerDto
from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto
from core.domain.errors.color_in_use_error import ColorInUseError
from core.domain.errors.pyrometer_not_found_error import PyrometerNotFoundError
from core.domain.models.pyrometer_overview_model import build_overviews
from interfaces.adapters.repositories.i_pyrometer_profile_repository import (
    IPyrometerProfileRepository,
)
from interfaces.adapters.repositories.i_reading_repository import IReadingRepository

PI12 = "C24C.F90D.0000"
PI14 = "B68A.1010.0000"


def build_use_case(
    mocker: MockerFixture, exists: bool
) -> tuple[SavePyrometerProfileUseCase, Mock, Mock]:
    readings = mocker.Mock(spec=IReadingRepository)
    readings.pyrometer_exists.return_value = exists
    readings.find_pyrometers.return_value = [
        PyrometerDto(PI12, "PI-12"),
        PyrometerDto(PI14, "PI-14"),
    ]
    profiles = mocker.Mock(spec=IPyrometerProfileRepository)
    profiles.find_all.return_value = []
    return SavePyrometerProfileUseCase(readings, profiles), readings, profiles


def test_should_save_the_profile_when_pyrometer_exists(mocker: MockerFixture) -> None:
    # Arrange
    use_case, _, profiles = build_use_case(mocker, exists=True)

    # Act
    use_case.execute(PI12, "Forno 2", "#e11d48", "termopar trocado", True)

    # Assert
    profiles.save.assert_called_once_with(
        PyrometerProfileDto(PI12, "Forno 2", "#e11d48", "termopar trocado", True)
    )


def test_should_check_existence_by_serial_when_saving(mocker: MockerFixture) -> None:
    # Arrange
    use_case, readings, _ = build_use_case(mocker, exists=True)

    # Act
    use_case.execute(PI12, None, None, None, True)

    # Assert
    readings.pyrometer_exists.assert_called_once_with(PI12)


def test_should_raise_and_save_nothing_when_pyrometer_does_not_exist(
    mocker: MockerFixture,
) -> None:
    # Arrange
    use_case, _, profiles = build_use_case(mocker, exists=False)

    # Act
    with pytest.raises(PyrometerNotFoundError) as raised:
        use_case.execute("ZZZZ.0000.0000", "Forno", None, None, True)

    # Assert
    assert raised.value.pyrometer_id == "ZZZZ.0000.0000"
    profiles.save.assert_not_called()


@pytest.mark.parametrize("empty", ["", "   "])
def test_should_store_none_when_nickname_and_note_are_blank(
    mocker: MockerFixture, empty: str
) -> None:
    # Arrange
    use_case, _, profiles = build_use_case(mocker, exists=True)

    # Act
    use_case.execute(PI12, empty, None, empty, True)

    # Assert
    profiles.save.assert_called_once_with(PyrometerProfileDto(PI12, None, None, None, True))


def test_should_trim_nickname_and_note_when_saving(mocker: MockerFixture) -> None:
    # Arrange
    use_case, _, profiles = build_use_case(mocker, exists=True)

    # Act
    use_case.execute(PI12, "  Forno 2 ", None, " nota  ", False)

    # Assert
    profiles.save.assert_called_once_with(PyrometerProfileDto(PI12, "Forno 2", None, "nota", False))


def test_should_raise_and_save_nothing_when_another_pyrometer_has_the_color(
    mocker: MockerFixture,
) -> None:
    # Arrange
    use_case, _, profiles = build_use_case(mocker, exists=True)
    profiles.find_all.return_value = [PyrometerProfileDto(PI14, None, "#e11d48", None, True)]

    # Act
    with pytest.raises(ColorInUseError) as raised:
        use_case.execute(PI12, None, "#E11D48", None, True)

    # Assert
    assert raised.value.color == "#E11D48"
    profiles.save.assert_not_called()


def test_should_raise_when_the_color_is_the_default_of_another_pyrometer(
    mocker: MockerFixture,
) -> None:
    # Arrange
    use_case, _, profiles = build_use_case(mocker, exists=True)
    default_of_pi14 = build_overviews(
        [PyrometerDto(PI12, "PI-12"), PyrometerDto(PI14, "PI-14")], []
    )[0].color

    # Act
    with pytest.raises(ColorInUseError):
        use_case.execute(PI12, None, default_of_pi14, None, True)

    # Assert
    profiles.save.assert_not_called()


def test_should_save_when_the_color_is_the_pyrometers_own(mocker: MockerFixture) -> None:
    # Arrange
    use_case, _, profiles = build_use_case(mocker, exists=True)
    profiles.find_all.return_value = [PyrometerProfileDto(PI12, None, "#e11d48", None, True)]

    # Act
    use_case.execute(PI12, "Forno 2", "#e11d48", None, True)

    # Assert
    profiles.save.assert_called_once_with(
        PyrometerProfileDto(PI12, "Forno 2", "#e11d48", None, True)
    )


def test_should_not_check_colors_when_no_color_is_given(mocker: MockerFixture) -> None:
    # Arrange
    use_case, readings, _ = build_use_case(mocker, exists=True)

    # Act
    use_case.execute(PI12, "Forno 2", None, None, True)

    # Assert
    readings.find_pyrometers.assert_not_called()
