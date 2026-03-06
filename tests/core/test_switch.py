import json
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from winreg import REG_DWORD

import pytest
import schedule
from astral import LocationInfo

from src.core.switch import Switch
from src.utils.path import Paths


@pytest.fixture
def paris():
    return LocationInfo(
        name="Paris",
        region="France",
        timezone="Europe/Paris",
        latitude=48.8333,
        longitude=2.33333,
    )


@pytest.fixture
def switch_obj(paris):
    return Switch(paris)


@pytest.fixture
def mock_sun_data():
    """Données solaires mockées à UTC pour la prévisibilité des tests."""
    return {
        "sunrise": datetime(2024, 6, 15, 6, 30, tzinfo=UTC),
        "sunset": datetime(2024, 6, 15, 20, 45, tzinfo=UTC),
    }


# ─── __init__ ────────────────────────────────────────────────────────────────


class TestSwitchInit:
    def test_city_assigned(self, paris):
        s = Switch(paris)
        assert s.city is paris

    def test_sun_hours_initialized_to_none(self, switch_obj):
        assert switch_obj.sun_hours == {
            "timestamp": None,
            "sunrise": None,
            "sunset": None,
        }

    def test_theme_initialized_to_none(self, switch_obj):
        assert switch_obj.theme is None


# ─── set_windows_theme ───────────────────────────────────────────────────────


class TestSetWindowsTheme:
    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_light_sets_apps_value_1(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_key = MagicMock()
        mock_openkey.return_value = mock_key
        switch_obj.set_windows_theme("light")
        mock_setvalue.assert_any_call(mock_key, "AppsUseLightTheme", 0, REG_DWORD, 1)

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_light_sets_system_value_1(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_key = MagicMock()
        mock_openkey.return_value = mock_key
        switch_obj.set_windows_theme("light")
        mock_setvalue.assert_any_call(mock_key, "SystemUsesLightTheme", 0, REG_DWORD, 1)

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_dark_sets_apps_value_0(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_key = MagicMock()
        mock_openkey.return_value = mock_key
        switch_obj.set_windows_theme("dark")
        mock_setvalue.assert_any_call(mock_key, "AppsUseLightTheme", 0, REG_DWORD, 0)

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_dark_sets_system_value_0(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_key = MagicMock()
        mock_openkey.return_value = mock_key
        switch_obj.set_windows_theme("dark")
        mock_setvalue.assert_any_call(mock_key, "SystemUsesLightTheme", 0, REG_DWORD, 0)

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_key_always_closed_on_success(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_key = MagicMock()
        mock_openkey.return_value = mock_key
        switch_obj.set_windows_theme("light")
        mock_key.Close.assert_called_once()

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_key_always_closed_on_invalid_theme(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_key = MagicMock()
        mock_openkey.return_value = mock_key
        switch_obj.set_windows_theme("invalid")
        mock_key.Close.assert_called_once()

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_invalid_theme_does_not_call_setvalue(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_openkey.return_value = MagicMock()
        switch_obj.set_windows_theme("invalid")
        mock_setvalue.assert_not_called()

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_broadcasts_two_messages_on_success(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_openkey.return_value = MagicMock()
        switch_obj.set_windows_theme("light")
        assert mock_windll.user32.SendNotifyMessageW.call_count == 2

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_no_broadcast_on_invalid_theme(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_openkey.return_value = MagicMock()
        switch_obj.set_windows_theme("bad_theme")
        mock_windll.user32.SendNotifyMessageW.assert_not_called()

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_theme_value_is_case_insensitive(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_key = MagicMock()
        mock_openkey.return_value = mock_key
        switch_obj.set_windows_theme("LIGHT")
        mock_setvalue.assert_any_call(mock_key, "AppsUseLightTheme", 0, REG_DWORD, 1)


# ─── switch_to_light_theme ───────────────────────────────────────────────────


class TestSwitchToLightTheme:
    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_switches_when_currently_dark(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_openkey.return_value = MagicMock()
        switch_obj.theme = "dark"
        switch_obj.switch_to_light_theme()
        assert switch_obj.theme == "light"

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_switches_when_theme_is_none(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_openkey.return_value = MagicMock()
        switch_obj.theme = None
        switch_obj.switch_to_light_theme()
        assert switch_obj.theme == "light"

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_skips_registry_when_already_light(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        switch_obj.theme = "light"
        switch_obj.switch_to_light_theme()
        mock_setvalue.assert_not_called()


# ─── switch_to_dark_theme ────────────────────────────────────────────────────


class TestSwitchToDarkTheme:
    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_switches_when_currently_light(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_openkey.return_value = MagicMock()
        switch_obj.theme = "light"
        switch_obj.switch_to_dark_theme()
        assert switch_obj.theme == "dark"

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_switches_when_theme_is_none(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        mock_openkey.return_value = MagicMock()
        switch_obj.theme = None
        switch_obj.switch_to_dark_theme()
        assert switch_obj.theme == "dark"

    @patch("src.core.switch.windll")
    @patch("src.core.switch.SetValueEx")
    @patch("src.core.switch.OpenKey")
    def test_skips_registry_when_already_dark(
        self, mock_openkey, mock_setvalue, mock_windll, switch_obj
    ):
        switch_obj.theme = "dark"
        switch_obj.switch_to_dark_theme()
        mock_setvalue.assert_not_called()


# ─── get_sun_hours ───────────────────────────────────────────────────────────


class TestGetSunHours:
    def test_reads_sunrise_from_valid_cache(self, switch_obj, tmp_path):
        today = datetime.today().strftime("%Y-%m-%d")
        cache = {"timestamp": today, "sunrise": "07:30:00", "sunset": "19:45:00"}
        (tmp_path / "ephemeris.json").write_text(json.dumps(cache))

        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = switch_obj.get_sun_hours()

        assert result["sunrise"] == "07:30"

    def test_reads_sunset_from_valid_cache(self, switch_obj, tmp_path):
        today = datetime.today().strftime("%Y-%m-%d")
        cache = {"timestamp": today, "sunrise": "07:30:00", "sunset": "19:45:00"}
        (tmp_path / "ephemeris.json").write_text(json.dumps(cache))

        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = switch_obj.get_sun_hours()

        assert result["sunset"] == "19:45"

    def test_reads_timestamp_from_valid_cache(self, switch_obj, tmp_path):
        today = datetime.today().strftime("%Y-%m-%d")
        cache = {"timestamp": today, "sunrise": "07:30:00", "sunset": "19:45:00"}
        (tmp_path / "ephemeris.json").write_text(json.dumps(cache))

        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = switch_obj.get_sun_hours()

        assert result["timestamp"] == today

    def test_ignores_stale_cache_and_recalculates(
        self, switch_obj, tmp_path, mock_sun_data
    ):
        stale = {"timestamp": "2000-01-01", "sunrise": "05:00:00", "sunset": "15:00:00"}
        (tmp_path / "ephemeris.json").write_text(json.dumps(stale))

        with (
            patch.object(Paths, "get_data_dir", return_value=tmp_path),
            patch("src.core.switch.sun", return_value=mock_sun_data),
        ):
            result = switch_obj.get_sun_hours()

        assert result["sunrise"] == "06:30"
        assert result["sunset"] == "20:45"

    def test_calculates_when_no_cache_file(self, switch_obj, tmp_path, mock_sun_data):
        with (
            patch.object(Paths, "get_data_dir", return_value=tmp_path),
            patch("src.core.switch.sun", return_value=mock_sun_data),
        ):
            result = switch_obj.get_sun_hours()

        assert result["sunrise"] == "06:30"
        assert result["sunset"] == "20:45"

    def test_saves_cache_file_after_calculation(
        self, switch_obj, tmp_path, mock_sun_data
    ):
        with (
            patch.object(Paths, "get_data_dir", return_value=tmp_path),
            patch("src.core.switch.sun", return_value=mock_sun_data),
        ):
            switch_obj.get_sun_hours()

        assert (tmp_path / "ephemeris.json").exists()

    def test_cached_file_has_today_timestamp(self, switch_obj, tmp_path, mock_sun_data):
        with (
            patch.object(Paths, "get_data_dir", return_value=tmp_path),
            patch("src.core.switch.sun", return_value=mock_sun_data),
        ):
            switch_obj.get_sun_hours()

        saved = json.loads((tmp_path / "ephemeris.json").read_text())
        assert saved["timestamp"] == datetime.today().strftime("%Y-%m-%d")

    def test_result_contains_all_keys(self, switch_obj, tmp_path):
        today = datetime.today().strftime("%Y-%m-%d")
        cache = {"timestamp": today, "sunrise": "07:00:00", "sunset": "20:00:00"}
        (tmp_path / "ephemeris.json").write_text(json.dumps(cache))

        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            result = switch_obj.get_sun_hours()

        assert {"sunrise", "sunset", "timestamp"} == set(result.keys())


# ─── update_sun_hours ────────────────────────────────────────────────────────


class TestUpdateSunHours:
    def test_schedules_exactly_two_switch_tasks(self, switch_obj, tmp_path):
        today = datetime.today().strftime("%Y-%m-%d")
        cache = {"timestamp": today, "sunrise": "07:00:00", "sunset": "20:00:00"}
        (tmp_path / "ephemeris.json").write_text(json.dumps(cache))

        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            switch_obj.update_sun_hours()

        assert len(schedule.get_jobs("switch-task")) == 2

    def test_clears_previous_switch_tasks_before_scheduling(self, switch_obj, tmp_path):
        # Pre-existing stale job
        schedule.every().day.at("05:00").do(lambda: None).tag("switch-task")

        today = datetime.today().strftime("%Y-%m-%d")
        cache = {"timestamp": today, "sunrise": "07:00:00", "sunset": "20:00:00"}
        (tmp_path / "ephemeris.json").write_text(json.dumps(cache))

        with patch.object(Paths, "get_data_dir", return_value=tmp_path):
            switch_obj.update_sun_hours()

        # Exactly 2 new jobs, stale one removed
        assert len(schedule.get_jobs("switch-task")) == 2

    def test_does_not_schedule_when_sun_hours_are_none(self, switch_obj):
        with patch.object(switch_obj, "get_sun_hours"):
            # sun_hours stays at initial None values
            switch_obj.update_sun_hours()

        assert len(schedule.get_jobs("switch-task")) == 0
