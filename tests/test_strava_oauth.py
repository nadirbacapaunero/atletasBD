from datetime import datetime

from src.strava_oauth import StravaOAuthHandler, StravaAPIClient


class DummyResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def test_get_authorization_url_includes_state():
    url = StravaOAuthHandler.get_authorization_url(123)
    assert "state=123" in url
    assert "client_id=" in url
    assert "redirect_uri=" in url


def test_exchange_code_for_token_returns_none_when_http_error(monkeypatch):
    def fake_post(url, data):
        return DummyResponse(400, {})

    monkeypatch.setattr("src.strava_oauth.requests.post", fake_post)
    assert StravaOAuthHandler.exchange_code_for_token("bad-code", "state") is None


def test_exchange_code_for_token_parses_success_response(monkeypatch):
    payload = {
        "access_token": "access123",
        "refresh_token": "refresh123",
        "expires_at": 9999999999,
        "athlete": {"id": 42, "firstname": "Jane", "lastname": "Doe"}
    }

    monkeypatch.setattr("src.strava_oauth.requests.post", lambda url, data: DummyResponse(200, payload))
    result = StravaOAuthHandler.exchange_code_for_token("code", "state")

    assert result["access_token"] == "access123"
    assert result["refresh_token"] == "refresh123"
    assert result["athlete_strava_id"] == 42
    assert result["athlete_name"] == "Jane Doe"


def test_strava_api_client_builds_headers_and_params(monkeypatch):
    captured = {}

    def fake_request(method, url, headers=None, params=None):
        captured["method"] = method
        captured["url"] = url
        captured["headers"] = headers
        captured["params"] = params
        return DummyResponse(200, ["ok"])

    monkeypatch.setattr("src.strava_oauth.requests.request", fake_request)
    client = StravaAPIClient("token123")

    assert client.get_athlete_profile() == ["ok"]
    assert captured["headers"]["Authorization"] == "Bearer token123"
    assert captured["url"].endswith("/athlete")
    assert captured["method"] == "GET"

    from_date = datetime(2023, 1, 1)
    result = client.get_activities(after=from_date, per_page=5)
    assert result == ["ok"]
    assert captured["params"]["per_page"] == 5
    assert captured["params"]["after"] == int(from_date.timestamp())
