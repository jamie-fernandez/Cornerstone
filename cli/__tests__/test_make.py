from __future__ import annotations

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from cli.commands import make
from cli.main import app

runner = CliRunner()


@pytest.fixture()
def temp_project(tmp_path, monkeypatch):
    """Set up temporary project structure for generator tests."""
    monkeypatch.setattr(make, "PROJECT_ROOT", str(tmp_path))

    # Setup app/api.py
    app_dir = tmp_path / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    api_file = app_dir / "api.py"
    api_file.write_text("class API:\n    def existing(self):\n        pass\n")

    # Setup app/models.py
    models_file = app_dir / "models.py"
    models_file.write_text("# models\n")

    # Setup ui/utils/bridge.mock.js
    ui_utils_dir = tmp_path / "ui" / "utils"
    ui_utils_dir.mkdir(parents=True, exist_ok=True)
    mock_file = ui_utils_dir / "bridge.mock.js"
    mock_file.write_text("export const mockApi = {\n    existing: () => ok({}),\n}\n")

    # Setup ui/router.js
    ui_dir = tmp_path / "ui"
    router_file = ui_dir / "router.js"
    router_file.write_text(
        "import PMain from '@/pages/PMain.vue'\n\nconst routes = [\n    {\n        path: '/',\n        component: PMain,\n    },\n]\n"
    )

    # Setup ui/pages/
    (ui_dir / "pages").mkdir(parents=True, exist_ok=True)

    return tmp_path


class TestMakeApi:
    def test_make_api_success(self, temp_project):
        result = runner.invoke(app, ["make", "api", "get_custom_stats"])
        assert result.exit_code == 0
        assert "get_custom_stats" in result.stdout

        api_text = (temp_project / "app" / "api.py").read_text()
        assert "def get_custom_stats(self):" in api_text
        assert "@bridge_method" in api_text

        mock_text = (temp_project / "ui" / "utils" / "bridge.mock.js").read_text()
        assert "get_custom_stats: () => ok(" in mock_text

    def test_make_api_already_exists(self, temp_project):
        runner.invoke(app, ["make", "api", "get_custom_stats"])
        result = runner.invoke(app, ["make", "api", "get_custom_stats"])
        assert "already exists" in result.stdout


class TestMakePage:
    def test_make_page_success(self, temp_project):
        result = runner.invoke(app, ["make", "page", "Settings"])
        assert result.exit_code == 0
        assert "PSettings.vue" in result.stdout

        page_file = temp_project / "ui" / "pages" / "PSettings.vue"
        assert page_file.exists()
        assert "<template>" in page_file.read_text()

        router_text = (temp_project / "ui" / "router.js").read_text()
        assert "import PSettings from '@/pages/PSettings.vue'" in router_text
        assert "path: '/settings'" in router_text

    def test_make_page_already_exists(self, temp_project):
        runner.invoke(app, ["make", "page", "Settings"])
        result = runner.invoke(app, ["make", "page", "Settings"])
        assert result.exit_code != 0
        assert "already exists" in result.stdout


class TestMakeModel:
    def test_make_model_success(self, temp_project):
        result = runner.invoke(
            app,
            ["make", "model", "Task", "--fields", "title:str,content:text,done:bool"],
        )
        assert result.exit_code == 0
        assert "Task" in result.stdout

        models_text = (temp_project / "app" / "models.py").read_text()
        assert "class Task(Base):" in models_text
        assert '__tablename__ = "tasks"' in models_text
        assert "title = Column(String" in models_text
        assert "content = Column(Text" in models_text
        assert "done = Column(Boolean" in models_text

    def test_make_model_with_migration(self, temp_project):
        with patch("cli.commands.db.migrations.db_migrate_command") as mock_mig:
            result = runner.invoke(app, ["make", "model", "Project", "--migrate"])
            assert result.exit_code == 0
            assert mock_mig.called
