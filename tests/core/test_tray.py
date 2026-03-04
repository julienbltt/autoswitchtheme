from unittest.mock import MagicMock, patch

import pytest

from src.core.tray import TrayApp
from src.utils.path import Paths


@pytest.fixture
def tray():
    return TrayApp()


@pytest.fixture
def tray_with_monitor(tray):
    monitor = MagicMock()
    monitor.theme = "light"
    monitor.sun_hours = {"sunrise": "07:00", "sunset": "20:00", "timestamp": "2024-06-15"}
    tray.theme_monitor = monitor
    return tray


# ─── __init__ ────────────────────────────────────────────────────────────────


class TestTrayAppInit:
    def test_icon_is_none(self, tray):
        assert tray.icon is None

    def test_theme_monitor_is_none(self, tray):
        assert tray.theme_monitor is None

    def test_running_is_true(self, tray):
        assert tray.running is True


# ─── load_icon ───────────────────────────────────────────────────────────────


class TestLoadIcon:
    def test_returns_none_when_icon_file_missing(self, tray, tmp_path):
        with patch.object(Paths, "get_assets_dir", return_value=tmp_path):
            result = tray.load_icon()
        assert result is None

    def test_returns_image_when_icon_file_exists(self, tray, tmp_path):
        icon_path = tmp_path / "icon.ico"
        icon_path.touch()
        mock_image = MagicMock()

        with patch.object(Paths, "get_assets_dir", return_value=tmp_path):
            with patch("src.core.tray.Image.open", return_value=mock_image):
                result = tray.load_icon()

        assert result is mock_image


# ─── on_force_light ──────────────────────────────────────────────────────────


class TestOnForceLight:
    def test_delegates_to_monitor(self, tray_with_monitor):
        tray_with_monitor.on_force_light(None, None)
        tray_with_monitor.theme_monitor.switch_to_light_theme.assert_called_once()

    def test_does_nothing_without_monitor(self, tray):
        tray.on_force_light(None, None)  # Must not raise


# ─── on_force_dark ───────────────────────────────────────────────────────────


class TestOnForceDark:
    def test_delegates_to_monitor(self, tray_with_monitor):
        tray_with_monitor.on_force_dark(None, None)
        tray_with_monitor.theme_monitor.switch_to_dark_theme.assert_called_once()

    def test_does_nothing_without_monitor(self, tray):
        tray.on_force_dark(None, None)  # Must not raise


# ─── on_quit ─────────────────────────────────────────────────────────────────


class TestOnQuit:
    def test_sets_running_to_false(self, tray):
        tray.on_quit(MagicMock(), None)
        assert tray.running is False

    def test_calls_icon_stop(self, tray):
        mock_icon = MagicMock()
        tray.on_quit(mock_icon, None)
        mock_icon.stop.assert_called_once()


# ─── on_show_status ──────────────────────────────────────────────────────────


class TestOnShowStatus:
    def test_does_nothing_without_monitor(self, tray):
        tray.on_show_status(None, None)  # Must not raise

    def test_opens_log_with_registry_handler(self, tray_with_monitor, tmp_path):
        log_file = tmp_path / "app.log"
        log_file.touch()

        mock_key_ctx = MagicMock()
        mock_key_ctx.__enter__ = MagicMock(return_value=MagicMock())
        mock_key_ctx.__exit__ = MagicMock(return_value=False)

        with patch.object(Paths, "get_log_file", return_value=log_file):
            with patch("src.core.tray.OpenKey", return_value=mock_key_ctx):
                with patch("src.core.tray.QueryValue", side_effect=["txtfile", 'notepad.exe "%1"']):
                    with patch("src.core.tray.run") as mock_run:
                        tray_with_monitor.on_show_status(None, None)
                        mock_run.assert_called_once()

    def test_falls_back_to_notepad_on_registry_error(self, tray_with_monitor, tmp_path):
        log_file = tmp_path / "app.log"
        log_file.touch()

        with patch.object(Paths, "get_log_file", return_value=log_file):
            with patch("src.core.tray.OpenKey", side_effect=OSError("no registry")):
                with patch("src.core.tray.run") as mock_run:
                    tray_with_monitor.on_show_status(None, None)
                    mock_run.assert_called_once_with(["notepad.exe", log_file])


# ─── setup_tray ──────────────────────────────────────────────────────────────


class TestSetupTray:
    def test_creates_pystray_icon(self, tray):
        mock_icon = MagicMock()
        with patch.object(tray, "load_icon", return_value=MagicMock()):
            with patch("src.core.tray.pystray.Icon", return_value=mock_icon) as mock_icon_cls:
                with patch("src.core.tray.pystray.Menu"):
                    with patch("src.core.tray.pystray.MenuItem"):
                        tray.setup_tray()
                        mock_icon_cls.assert_called_once()

    def test_returns_icon_instance(self, tray):
        mock_icon = MagicMock()
        with patch.object(tray, "load_icon", return_value=MagicMock()):
            with patch("src.core.tray.pystray.Icon", return_value=mock_icon):
                with patch("src.core.tray.pystray.Menu"):
                    with patch("src.core.tray.pystray.MenuItem"):
                        result = tray.setup_tray()
        assert result is mock_icon

    def test_icon_stored_on_self(self, tray):
        mock_icon = MagicMock()
        with patch.object(tray, "load_icon", return_value=MagicMock()):
            with patch("src.core.tray.pystray.Icon", return_value=mock_icon):
                with patch("src.core.tray.pystray.Menu"):
                    with patch("src.core.tray.pystray.MenuItem"):
                        tray.setup_tray()
        assert tray.icon is mock_icon
