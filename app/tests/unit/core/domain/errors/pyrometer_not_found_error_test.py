from core.domain.errors.pyrometer_not_found_error import PyrometerNotFoundError


def test_should_name_the_serial_when_building_the_message() -> None:
    # Arrange
    serial = "C24C.F90D.0000"

    # Act
    error = PyrometerNotFoundError(serial)

    # Assert
    assert str(error) == "pirometro 'C24C.F90D.0000' nao encontrado"


def test_should_keep_the_serial_when_raised() -> None:
    # Arrange
    serial = "C24C.F90D.0000"

    # Act
    error = PyrometerNotFoundError(serial)

    # Assert
    assert error.pyrometer_id == serial
