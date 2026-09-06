from __future__ import annotations

import json
import sys
from unittest.mock import patch

import pytest

from cli.commands import init

SAMPLE_PYPROJECT = """[project]
name = "cornerstone"
version = "0.0.0"
description = ""
dependencies = []

[tool.app]
display-name = "Cornerstone"
"""

SAMPLE_PYPROJECT_NO_DISPLAY_NAME = """[project]
name = "cornerstone"
version = "0.0.0"
description = ""
"""


@pytest.fixture()
def rebrand(tmp_path, monkeypatch):
    """A throwaway project root that init.py rewrites instead of the real one."""
    monkeypatch.setattr(init, "PROJECT_ROOT", str(tmp_path))
    return tmp_path


class TestSlugify:
    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("My App", "my-app"),
            ("My  App--", "my-app"),
            ("App2 3", "app2-3"),
            ("Café", "caf"),
            ("!!!", "app"),
            ("", "app"),
        ],
    )
    def test_slugify(self, name, expected):
        assert init.slugify(name) == expected


class TestTomlEscape:
    def test_escapes_quotes_and_backslashes(self):
        assert init._toml_escape('a"b\\c') == r"a\"b\\c"

    def test_plain_strings_pass_through(self):
        assert init._toml_escape("my-app") == "my-app"


class TestUpdatePyproject:
    def test_rewrites_identity_lines(self, rebrand):
        (rebrand / "pyproject.toml").write_text(SAMPLE_PYPROJECT)

        init.update_pyproject("My App", "my-app", "My description")

        text = (rebrand / "pyproject.toml").read_text()
        assert 'name = "my-app"' in text
        assert f'version = "{init.INITIAL_VERSION}"' in text
        assert 'description = "My description"' in text
        assert 'display-name = "My App"' in text
        assert "Cornerstone" not in text

    def test_special_characters_are_written_literally(self, rebrand):
        """Values containing regex tokens (``\\1``) or quotes must not corrupt TOML."""
        (rebrand / "pyproject.toml").write_text(SAMPLE_PYPROJECT)

        init.update_pyproject("My App", "my-app", 'back\\slash "quote" \\1')

        text = (rebrand / "pyproject.toml").read_text()
        assert r'description = "back\\slash \"quote\" \\1"' in text

    def test_adds_tool_app_section_when_missing(self, rebrand):
        (rebrand / "pyproject.toml").write_text(SAMPLE_PYPROJECT_NO_DISPLAY_NAME)

        init.update_pyproject("My App", "my-app", "")

        text = (rebrand / "pyproject.toml").read_text()
        assert "[tool.app]" in text
        assert 'display-name = "My App"' in text

    def test_rewrites_scripts_section_with_slug_default(self, rebrand):
        (rebrand / "pyproject.toml").write_text(SAMPLE_PYPROJECT)

        init.update_pyproject("My App", "my-app", "My description")

        text = (rebrand / "pyproject.toml").read_text()
        assert "[project.scripts]" in text
        assert 'my-app = "cli:app"' in text

    def test_rewrites_scripts_section_with_single_alias(self, rebrand):
        (rebrand / "pyproject.toml").write_text(SAMPLE_PYPROJECT)

        init.update_pyproject("My App", "my-app", "My description", aliases=["tf"])

        text = (rebrand / "pyproject.toml").read_text()
        assert "[project.scripts]" in text
        assert 'my-app = "cli:app"' in text
        assert 'tf = "cli:app"' in text

    def test_rewrites_scripts_section_with_multiple_aliases_and_deduplication(
        self, rebrand
    ):
        (rebrand / "pyproject.toml").write_text(
            SAMPLE_PYPROJECT
            + '\n[project.scripts]\ncornerstone = "cli:app"\nstone = "cli:app"\n'
        )

        init.update_pyproject(
            "Note Forge",
            "note-forge",
            "My description",
            aliases=["nf", "stone", "nf", "Note Forge", ""],
        )

        text = (rebrand / "pyproject.toml").read_text()
        assert 'cornerstone = "cli:app"' not in text
        assert 'note-forge = "cli:app"' in text
        assert 'nf = "cli:app"' in text
        assert 'stone = "cli:app"' in text
        # Count occurrences to verify deduplication
        assert text.count('nf = "cli:app"') == 1
        assert text.count('note-forge = "cli:app"') == 1


class TestUpdatePackageJson:
    def test_updates_name_version_description(self, rebrand):
        package = {
            "name": "cornerstone",
            "version": "0.0.0",
            "description": "",
            "private": True,
        }
        (rebrand / "package.json").write_text(json.dumps(package, indent=4) + "\n")

        init.update_package_json("my-app", "My description")

        data = json.loads((rebrand / "package.json").read_text())
        assert data["name"] == "my-app"
        assert data["version"] == init.INITIAL_VERSION
        assert data["description"] == "My description"
        assert data["private"] is True

    def test_output_is_four_space_indented_with_trailing_newline(self, rebrand):
        (rebrand / "package.json").write_text('{"name": "cornerstone"}')

        init.update_package_json("my-app", "")

        text = (rebrand / "package.json").read_text()
        assert text.startswith("{\n    ")
        assert text.endswith("\n")


class TestUpdateDocs:
    def test_swaps_brand_and_upstream_url_in_order(self, rebrand):
        readme = "# Cornerstone\ncornerstone docs\nhttps://gitlab.com/jnf-desktop-apps/cornerstone\n"
        (rebrand / "README.md").write_text(readme)

        init.update_docs("My App", "my-app")

        text = (rebrand / "README.md").read_text()
        assert "My App" in text
        assert "my-app" in text
        assert (rebrand / ".cornerstone" / "README.md").exists()
        assert (rebrand / ".cornerstone" / "UPSTREAM.md").exists()
        upstream_text = (rebrand / ".cornerstone" / "UPSTREAM.md").read_text()
        assert "https://gitlab.com/jnf-desktop-apps/cornerstone" in upstream_text
        assert "My App" in upstream_text

    def test_rewrites_every_existing_doc_file(self, rebrand):
        for rel in init.DOC_FILES:
            path = rebrand / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Cornerstone")

        init.update_docs("My App", "my-app")

        for rel in init.DOC_FILES:
            assert "My App" in (rebrand / rel).read_text()

    def test_missing_doc_files_are_skipped(self, rebrand):
        init.update_docs("My App", "my-app")  # must not raise


class TestConfigureCI:
    def test_ci_github_only(self, rebrand):
        (rebrand / ".gitlab-ci.yml").write_text("gitlab")
        (rebrand / ".gitlab").mkdir(parents=True)
        (rebrand / ".github").mkdir(parents=True)

        init.configure_ci_workflows("github")
        assert not (rebrand / ".gitlab-ci.yml").exists()
        assert not (rebrand / ".gitlab").exists()
        assert (rebrand / ".github").exists()

    def test_ci_gitlab_only(self, rebrand):
        (rebrand / ".gitlab-ci.yml").write_text("gitlab")
        (rebrand / ".github").mkdir(parents=True)

        init.configure_ci_workflows("gitlab")
        assert not (rebrand / ".github").exists()
        assert (rebrand / ".gitlab-ci.yml").exists()

    def test_ci_both(self, rebrand):
        (rebrand / ".gitlab-ci.yml").write_text("gitlab")
        (rebrand / ".github").mkdir(parents=True)

        init.configure_ci_workflows("both")
        assert (rebrand / ".github").exists()
        assert (rebrand / ".gitlab-ci.yml").exists()


class TestGitReinit:
    def test_reinitialize_git_repository(self, rebrand):
        (rebrand / ".git").mkdir(parents=True)
        with patch("subprocess.run") as mock_run:
            init.reinitialize_git_repository("My App")
            assert mock_run.called


class TestCleanExamples:
    def test_writes_minimal_api_and_main_page(self, rebrand):
        (rebrand / "app").mkdir()
        (rebrand / "ui" / "pages").mkdir(parents=True)

        init.clean_examples("My App")

        api_py = (rebrand / "app" / "api.py").read_text()
        pmain = (rebrand / "ui" / "pages" / "PMain.vue").read_text()
        assert "class API" in api_py
        assert "My App" in pmain


class TestMain:
    def test_rebrands_and_cleans_in_one_step(self, rebrand, monkeypatch, capsys):
        (rebrand / "pyproject.toml").write_text(SAMPLE_PYPROJECT)
        (rebrand / "package.json").write_text('{"name": "cornerstone"}')
        (rebrand / "README.md").write_text("# Cornerstone")
        (rebrand / "app").mkdir()
        (rebrand / "ui" / "pages").mkdir(parents=True)
        monkeypatch.setattr(sys, "argv", ["init.py", "My", "App", "--clean-examples"])

        init.main()

        assert 'name = "my-app"' in (rebrand / "pyproject.toml").read_text()
        assert json.loads((rebrand / "package.json").read_text())["name"] == "my-app"
        assert "My App" in (rebrand / "README.md").read_text()
        assert "class API" in (rebrand / "app" / "api.py").read_text()
        assert "My App" in (rebrand / "ui" / "pages" / "PMain.vue").read_text()
        out = capsys.readouterr().out
        assert "Rebranding" in out
        assert "Removed example code" in out
        assert "Done" in out

    def test_main_with_alias_flags(self, rebrand, monkeypatch, capsys):
        (rebrand / "pyproject.toml").write_text(SAMPLE_PYPROJECT)
        (rebrand / "package.json").write_text('{"name": "cornerstone"}')
        (rebrand / "README.md").write_text("# Cornerstone")
        (rebrand / "app").mkdir()
        (rebrand / "ui" / "pages").mkdir(parents=True)
        monkeypatch.setattr(
            sys,
            "argv",
            ["init.py", "Task", "Flow", "--alias", "tf", "-a", "stone"],
        )

        init.main()

        pyproject_text = (rebrand / "pyproject.toml").read_text()
        assert 'task-flow = "cli:app"' in pyproject_text
        assert 'tf = "cli:app"' in pyproject_text
        assert 'stone = "cli:app"' in pyproject_text
        out = capsys.readouterr().out
        assert "Registered CLI commands: task-flow, tf, stone" in out

    def test_rejects_blank_name(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["init.py", "   "])

        with pytest.raises(SystemExit) as exc:
            init.main()

        assert exc.value.code == 2
