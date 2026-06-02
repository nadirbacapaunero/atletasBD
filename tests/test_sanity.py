import pytest

from src.config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, ENCRYPTION_KEY
from src.oauth_server import app
from src.strava_oauth import StravaAPIClient


def test_config_has_required_values():
    assert STRAVA_CLIENT_ID is not None and STRAVA_CLIENT_ID != ""
    assert STRAVA_CLIENT_SECRET is not None and STRAVA_CLIENT_SECRET != ""
    assert ENCRYPTION_KEY is not None and ENCRYPTION_KEY != ""


def test_oauth_server_app_loads():
    assert app is not None
    assert hasattr(app, 'routes')


def test_strava_api_client_authorization_header():
    client = StravaAPIClient("dummy_token")
    assert client.headers["Authorization"] == "Bearer dummy_token"
