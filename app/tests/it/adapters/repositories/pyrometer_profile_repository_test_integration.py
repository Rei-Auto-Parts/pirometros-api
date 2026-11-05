from sqlalchemy import Engine, text

from adapters.repositories.pyrometer_profile_repository import PyrometerProfileRepository
from core.domain.dtos.pyrometer_profile_dto import PyrometerProfileDto
from infra.tools.database_tool import build_engine

PI_12 = "C24C.F90D.0000"


def test_should_return_nothing_when_no_profile_was_saved(clean_readings: Engine) -> None:
    # Arrange
    repository = PyrometerProfileRepository(clean_readings)

    # Act
    result = repository.find_all()

    # Assert
    assert result == []


def test_should_return_the_saved_profile_when_finding_all(clean_readings: Engine) -> None:
    # Arrange
    repository = PyrometerProfileRepository(clean_readings)
    profile = PyrometerProfileDto(PI_12, "Forno 2", "#e11d48", "termopar trocado", False)

    # Act
    repository.save(profile)

    # Assert
    assert repository.find_all() == [profile]


def test_should_replace_instead_of_duplicate_when_saving_the_same_serial_twice(
    clean_readings: Engine,
) -> None:
    # Arrange
    repository = PyrometerProfileRepository(clean_readings)
    repository.save(PyrometerProfileDto(PI_12, "Forno 2", None, None, True))

    # Act
    repository.save(PyrometerProfileDto(PI_12, "Forno 3", "#2563eb", None, False))

    # Assert
    assert repository.find_all() == [PyrometerProfileDto(PI_12, "Forno 3", "#2563eb", None, False)]


def test_should_keep_the_profile_when_the_connection_is_recreated(
    clean_readings: Engine,
) -> None:
    # Arrange
    profile = PyrometerProfileDto(PI_12, "Forno 2", None, None, True)
    PyrometerProfileRepository(clean_readings).save(profile)
    url = clean_readings.url.render_as_string(hide_password=False)

    # Act
    result = PyrometerProfileRepository(build_engine(url)).find_all()

    # Assert
    assert result == [profile]


def test_should_not_touch_receiver_data_when_saving(clean_readings: Engine) -> None:
    # Arrange
    repository = PyrometerProfileRepository(clean_readings)

    # Act
    repository.save(PyrometerProfileDto(PI_12, "Forno 2", None, None, True))

    # Assert
    with clean_readings.connect() as connection:
        count = connection.execute(text("SELECT count(*) FROM public.receiver_data")).scalar_one()
    assert count == 0
