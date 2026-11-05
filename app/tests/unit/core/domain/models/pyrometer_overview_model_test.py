from core.domain.constants.pyrometer_constants import PALETTE
from core.domain.dtos.pyrometer_dto import PyrometerDto
from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto
from core.domain.models.default_color_model import assign_default_colors
from core.domain.models.pyrometer_overview_model import build_overviews

PI12 = "C24C.F90D.0000"
PI14 = "B68A.1010.0000"
PYROMETERS = [PyrometerDto(PI12, "PI-12"), PyrometerDto(PI14, "PI-14")]


def test_should_apply_defaults_when_there_is_no_profile() -> None:
    # Arrange / Act
    result = build_overviews([PyrometerDto(PI12, "PI-12")], [])

    # Assert
    assert (result[0].nickname, result[0].note, result[0].active) == (None, None, True)
    assert result[0].color == assign_default_colors([PI12])[PI12]


def test_should_order_by_serial_when_building() -> None:
    # Arrange / Act
    result = build_overviews(PYROMETERS, [])

    # Assert
    assert [item.id for item in result] == [PI14, PI12]


def test_should_keep_the_chosen_color_when_the_profile_has_one() -> None:
    # Arrange
    profile = PyrometerProfileDto(PI12, "Forno 2", "#e11d48", "nota", False)

    # Act
    item = build_overviews(PYROMETERS, [profile])[1]

    # Assert
    assert (item.nickname, item.color, item.note, item.active) == (
        "Forno 2",
        "#e11d48",
        "nota",
        False,
    )


def test_should_never_give_a_default_color_equal_to_a_chosen_one() -> None:
    # Arrange
    default_of_pi14 = assign_default_colors([PI14])[PI14]
    profile = PyrometerProfileDto(PI12, None, default_of_pi14, None, True)

    # Act
    result = {item.id: item.color for item in build_overviews(PYROMETERS, [profile])}

    # Assert
    assert result[PI12] == default_of_pi14
    assert result[PI14] != default_of_pi14


def test_should_give_every_pyrometer_a_different_color_when_the_palette_allows() -> None:
    # Arrange
    pyrometers = [PyrometerDto(f"SERIAL-{index:03d}", None) for index in range(len(PALETTE))]

    # Act
    colors = {item.color for item in build_overviews(pyrometers, [])}

    # Assert
    assert len(colors) == len(PALETTE)


def test_should_ignore_a_chosen_color_in_a_different_letter_case() -> None:
    # Arrange
    chosen = PALETTE[0].upper()
    profile = PyrometerProfileDto(PI12, None, chosen, None, True)

    # Act
    result = {item.id: item.color for item in build_overviews(PYROMETERS, [profile])}

    # Assert
    assert result[PI14].lower() != chosen.lower()
