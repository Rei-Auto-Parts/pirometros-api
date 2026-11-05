from core.domain.constants.pyrometer_constants import PALETTE
from core.domain.models.default_color_model import assign_default_colors


def test_should_return_the_same_color_when_called_twice_for_the_same_serials() -> None:
    # Arrange
    serials = ["C24C.F90D.0000", "B68A.1010.0000"]

    # Act
    first = assign_default_colors(serials)
    second = assign_default_colors(serials)

    # Assert
    assert first == second


def test_should_ignore_input_order_when_assigning_colors() -> None:
    # Arrange
    serials = ["C24C.F90D.0000", "B68A.1010.0000", "A001.0000.0000"]

    # Act
    forward = assign_default_colors(serials)
    backward = assign_default_colors(list(reversed(serials)))

    # Assert
    assert forward == backward


def test_should_pick_different_colors_when_serials_collide_in_the_palette() -> None:
    # Arrange
    serials = [f"SERIAL-{index:03d}" for index in range(len(PALETTE))]

    # Act
    colors = assign_default_colors(serials)

    # Assert
    assert len(set(colors.values())) == len(PALETTE)


def test_should_only_use_palette_colors_when_assigning() -> None:
    # Arrange
    serials = ["C24C.F90D.0000", "B68A.1010.0000"]

    # Act
    colors = assign_default_colors(serials)

    # Assert
    assert set(colors.values()) <= set(PALETTE)


def test_should_reuse_colors_when_there_are_more_serials_than_colors() -> None:
    # Arrange
    serials = [f"SERIAL-{index:03d}" for index in range(len(PALETTE) + 3)]

    # Act
    colors = assign_default_colors(serials)

    # Assert
    assert set(colors) == set(serials)


def test_should_return_nothing_when_there_are_no_serials() -> None:
    # Arrange
    serials: list[str] = []

    # Act
    colors = assign_default_colors(serials)

    # Assert
    assert colors == {}
