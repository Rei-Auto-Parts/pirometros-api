from core.domain.errors.color_in_use_error import ColorInUseError


def test_should_name_the_color_when_building_the_message() -> None:
    # Arrange
    color = "#e11d48"

    # Act
    error = ColorInUseError(color)

    # Assert
    assert str(error) == "a cor '#e11d48' ja esta em uso por outro pirometro"
    assert error.color == color
