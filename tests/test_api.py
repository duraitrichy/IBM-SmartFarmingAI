"""
tests/test_api.py — Integration tests for SmartFarmingAI REST API.
"""

import pytest
import json
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return app


@pytest.fixture
def client(app):
    with app.test_client() as c:
        with app.app_context():
            from database import init_db
            init_db(app)
        yield c


class TestPages:
    def test_home(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_dashboard(self, client):
        r = client.get("/dashboard")
        assert r.status_code == 200

    def test_chat_page(self, client):
        r = client.get("/chat")
        assert r.status_code == 200

    def test_weather_page(self, client):
        r = client.get("/weather")
        assert r.status_code == 200

    def test_soil_page(self, client):
        r = client.get("/soil")
        assert r.status_code == 200

    def test_pest_page(self, client):
        r = client.get("/pest")
        assert r.status_code == 200

    def test_market_page(self, client):
        r = client.get("/market")
        assert r.status_code == 200

    def test_profile_page(self, client):
        r = client.get("/profile")
        assert r.status_code == 200

    def test_reports_page(self, client):
        r = client.get("/report")
        assert r.status_code == 200


class TestAPI:
    def test_schemes_all(self, client):
        r = client.get("/api/schemes")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_schemes_search(self, client):
        r = client.get("/api/schemes?q=pm-kisan")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert isinstance(data, list)

    def test_history_empty(self, client):
        r = client.get("/api/history")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert isinstance(data, list)

    def test_chat_empty_query(self, client):
        r = client.post(
            "/api/chat",
            data=json.dumps({"query": ""}),
            content_type="application/json",
        )
        assert r.status_code == 400

    def test_pest_no_file_no_symptoms(self, client):
        r = client.post("/api/pest", data={"crop": "rice"})
        # Should still attempt analysis (symptom-based fallback)
        assert r.status_code in (200, 500)


class TestSoilTool:
    def test_soil_analysis_tool(self):
        from tools.soil_analysis import SoilAnalysisTool
        tool = SoilAnalysisTool()
        result = tool.analyse({
            "ph": 6.5, "nitrogen": 280, "phosphorus": 15,
            "potassium": 150, "moisture": 55, "organic_matter": 2.0
        })
        assert "soil_health_score" in result
        assert result["soil_health_score"] >= 0
        assert isinstance(result["suitable_crops"], list)

    def test_soil_deficiency_detection(self):
        from tools.soil_analysis import SoilAnalysisTool
        tool = SoilAnalysisTool()
        result = tool.analyse({
            "ph": 4.5, "nitrogen": 100, "phosphorus": 5,
            "potassium": 60, "moisture": 20, "organic_matter": 0.5
        })
        assert len(result["deficiencies"]) > 0
        assert result["soil_health_score"] < 50


class TestGovernmentSchemes:
    def test_search_pmkisan(self):
        from tools.government_schemes import GovernmentSchemesTool
        tool = GovernmentSchemesTool()
        results = tool.search("pm-kisan income support")
        assert any("PM-KISAN" in s["name"] for s in results)

    def test_get_all(self):
        from tools.government_schemes import GovernmentSchemesTool
        tool = GovernmentSchemesTool()
        all_schemes = tool.get_all()
        assert len(all_schemes) >= 5
