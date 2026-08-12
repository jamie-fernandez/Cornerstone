import pytest

from app.api import API
from app.decorators import bridge_method
from app.exceptions import BridgeError


#  use command: pytest app/__tests__/
class TestAPI:
    def test_api_import(self):
        try:
            from app import API
        except ImportError as e:
            pytest.fail(f"Failed to import API: {e}")

        api = API()
        response = api.get_app_configuration()

        assert response["status"] == "success"
        assert isinstance(response["data"], dict)

    def test_database_connection(self, db):
        api = API()
        response = api.test_database_connection()

        assert response["status"] == "success"
        assert response["data"]["message"] == "Database connection OK"


class TestBridgeMethod:
    def test_success_envelope(self):
        @bridge_method
        def succeeds():
            return {"key": "value"}

        assert succeeds() == {"status": "success", "data": {"key": "value"}}

    def test_unexpected_error_does_not_leak_internals(self):
        @bridge_method
        def fails():
            raise ValueError("secret internals")

        response = fails()

        assert response["status"] == "error"
        assert response["message"] == "An internal error occurred"

    def test_bridge_error_message_reaches_frontend(self):
        @bridge_method
        def fails():
            raise BridgeError("safe, user-facing message")

        response = fails()

        assert response["status"] == "error"
        assert response["message"] == "safe, user-facing message"
