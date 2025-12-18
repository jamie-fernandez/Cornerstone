import pytest


#  use command: pytest app/__tests__/
class TestApi:
    def test_api_import(self):
        try:
            from app import Api  # noqa: F401
        except ImportError as e:
            pytest.fail(f"Failed to import Api: {e}")

        api = Api()
        configuration = api.get_app_configuration()

        assert configuration is not None
        assert isinstance(configuration, dict)
