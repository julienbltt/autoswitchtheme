import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.path import Paths


class TestGetAppDir:
    def test_returns_path_instance(self):
        assert isinstance(Paths.get_app_dir(), Path)

    def test_is_project_root(self):
        # path.py is at src/utils/path.py → root is 3 levels up
        result = Paths.get_app_dir()
        assert (result / "src").is_dir()


class TestGetAssetsDir:
    def test_is_named_assets(self):
        assert Paths.get_assets_dir().name == "assets"

    def test_is_child_of_app_dir(self):
        assert Paths.get_assets_dir().parent == Paths.get_app_dir()


class TestGetDataDir:
    def test_uses_programdata_env_var(self, tmp_path):
        with patch.dict(os.environ, {"PROGRAMDATA": str(tmp_path)}):
            result = Paths.get_data_dir()
        assert result == tmp_path / "AutoSwitchTheme"

    def test_creates_directory_if_missing(self, tmp_path):
        with patch.dict(os.environ, {"PROGRAMDATA": str(tmp_path)}):
            result = Paths.get_data_dir()
        assert result.is_dir()

    def test_returns_path_containing_app_name(self):
        result = Paths.get_data_dir()
        assert "AutoSwitchTheme" in str(result)

    def test_fallback_when_programdata_missing(self, tmp_path):
        env = {k: v for k, v in os.environ.items() if k != "PROGRAMDATA"}
        with patch.dict(os.environ, env, clear=True):
            result = Paths.get_data_dir()
        assert "AutoSwitchTheme" in str(result)


class TestGetUserDataDir:
    def test_uses_appdata_env_var(self, tmp_path):
        with patch.dict(os.environ, {"APPDATA": str(tmp_path)}):
            result = Paths.get_user_data_dir()
        assert result == tmp_path / "AutoSwitchTheme"

    def test_creates_directory_if_missing(self, tmp_path):
        with patch.dict(os.environ, {"APPDATA": str(tmp_path)}):
            result = Paths.get_user_data_dir()
        assert result.is_dir()

    def test_fallback_uses_getlogin(self, tmp_path):
        env = {k: v for k, v in os.environ.items() if k != "APPDATA"}
        with patch.dict(os.environ, env, clear=True):
            with patch("src.utils.path.getlogin", return_value="testuser"):
                # Prevent actual mkdir on the protected C:\Users\testuser path
                with patch.object(Path, "mkdir"):
                    result = Paths.get_user_data_dir()
        assert "AutoSwitchTheme" in str(result)


class TestGetConfigFile:
    def test_filename_is_settings_ini(self, tmp_path):
        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = Paths.get_config_file()
        assert result.name == "settings.ini"

    def test_parent_dir_is_named_config(self, tmp_path):
        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = Paths.get_config_file()
        assert result.parent.name == "config"

    def test_creates_config_directory(self, tmp_path):
        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = Paths.get_config_file()
        assert result.parent.is_dir()


class TestGetLogFile:
    def test_filename_is_app_log(self, tmp_path):
        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = Paths.get_log_file()
        assert result.name == "app.log"

    def test_parent_dir_is_named_logs(self, tmp_path):
        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = Paths.get_log_file()
        assert result.parent.name == "logs"

    def test_creates_logs_directory(self, tmp_path):
        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = Paths.get_log_file()
        assert result.parent.is_dir()
