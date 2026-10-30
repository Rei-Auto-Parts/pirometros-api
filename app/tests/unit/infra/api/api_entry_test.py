import uvicorn
from fastapi import FastAPI
from pytest_mock import MockerFixture

from infra.api.api_entry import ApiEntry


def test_should_run_before_start_then_serve_when_entry_runs(mocker: MockerFixture) -> None:
    # Arrange
    app = FastAPI()
    calls = mocker.Mock()
    mocker.patch.object(uvicorn, "run", calls.serve)
    entry = ApiEntry(app, "0.0.0.0", 9000, calls.before_start)

    # Act
    entry.run()

    # Assert
    assert [call[0] for call in calls.mock_calls] == ["before_start", "serve"]
    calls.before_start.assert_called_once_with()
    calls.serve.assert_called_once_with(app, host="0.0.0.0", port=9000)
