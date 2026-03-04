from datetime import datetime, time
from unittest.mock import MagicMock, patch

import pytest


def _make_tray_app(switch_instance):
    """Return a MagicMock TrayApp whose running flag stops the scheduler loop."""
    tray_app = MagicMock()
    tray_app.running = False
    tray_app.theme_monitor = switch_instance
    return tray_app


def _run_main_thread(switch_instance, now_time: time, online: bool = False):
    """
    Helper: run main_thread with controlled time and connectivity.

    The Switch mock's sun_hours must already be set by the caller.
    """
    from main import main_thread

    tray_app = _make_tray_app(switch_instance)

    get_side_effect = MagicMock() if online else Exception("no internet")

    with patch("main.schedule"):
        with patch("main.get", side_effect=get_side_effect):
            with patch("main.Switch", return_value=switch_instance):
                with patch("main.configurator") as mock_cfg:
                    mock_cfg.getfloat.side_effect = [48.8333, 2.33333]
                    mock_cfg.get.side_effect = ["Paris", "France", "Europe/Paris"]
                    mock_cfg.getboolean.return_value = False
                    with patch("main.datetime") as mock_dt:
                        mock_dt.now.return_value.time.return_value = now_time
                        mock_dt.strptime = datetime.strptime
                        main_thread(tray_app)

    return switch_instance


# ─── Connectivity ─────────────────────────────────────────────────────────────


class TestConnectivity:
    def test_continues_when_no_internet(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        # Should not raise even with no network
        _run_main_thread(switch, now_time=time(12, 0), online=False)

    def test_runs_with_internet_connected(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "city": "Paris",
            "region": "Île-de-France",
            "timezone": "Europe/Paris",
            "loc": "48.8333,2.33333",
        }

        from main import main_thread

        tray_app = _make_tray_app(switch)

        with patch("main.schedule"):
            with patch("main.get", return_value=mock_response):
                with patch("main.Switch", return_value=switch):
                    with patch("main.configurator") as mock_cfg:
                        mock_cfg.getfloat.side_effect = [48.8333, 2.33333]
                        mock_cfg.get.side_effect = ["Paris", "Île-de-France", "Europe/Paris"]
                        mock_cfg.getboolean.return_value = False
                        with patch("main.open", MagicMock()):
                            with patch("main.datetime") as mock_dt:
                                mock_dt.now.return_value.time.return_value = time(12, 0)
                                mock_dt.strptime = datetime.strptime
                                main_thread(tray_app)


# ─── Location fallback ────────────────────────────────────────────────────────


class TestLocationFallback:
    def test_uses_paris_defaults_when_coordinates_are_zero(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        from main import main_thread

        tray_app = _make_tray_app(switch)

        with patch("main.schedule"):
            with patch("main.get", side_effect=Exception("no internet")):
                with patch("main.Switch", return_value=switch):
                    with patch("main.configurator") as mock_cfg:
                        # Both coords = 0.0 → Paris fallback
                        mock_cfg.getfloat.side_effect = [0.0, 0.0]
                        mock_cfg.getboolean.return_value = False
                        with patch("main.LocationInfo") as mock_loc:
                            with patch("main.datetime") as mock_dt:
                                mock_dt.now.return_value.time.return_value = time(12, 0)
                                mock_dt.strptime = datetime.strptime
                                main_thread(tray_app)

                        call_kwargs = mock_loc.call_args
                        assert call_kwargs.kwargs.get("latitude") == 48.8333

    def test_uses_configured_location_when_coordinates_set(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        from main import main_thread

        tray_app = _make_tray_app(switch)

        with patch("main.schedule"):
            with patch("main.get", side_effect=Exception("no internet")):
                with patch("main.Switch", return_value=switch):
                    with patch("main.configurator") as mock_cfg:
                        mock_cfg.getfloat.side_effect = [43.2965, 5.3698]
                        mock_cfg.get.side_effect = ["Marseille", "PACA", "Europe/Paris"]
                        mock_cfg.getboolean.return_value = False
                        with patch("main.LocationInfo") as mock_loc:
                            with patch("main.datetime") as mock_dt:
                                mock_dt.now.return_value.time.return_value = time(12, 0)
                                mock_dt.strptime = datetime.strptime
                                main_thread(tray_app)

                        call_kwargs = mock_loc.call_args
                        assert call_kwargs.kwargs.get("latitude") == 43.2965


# ─── Theme switching at startup ───────────────────────────────────────────────


class TestThemeSwitchAtStartup:
    def test_switches_to_light_during_daytime(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        _run_main_thread(switch, now_time=time(12, 0))

        switch.switch_to_light_theme.assert_called_once()
        switch.switch_to_dark_theme.assert_not_called()

    def test_switches_to_dark_during_nighttime(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        _run_main_thread(switch, now_time=time(23, 0))

        switch.switch_to_dark_theme.assert_called_once()
        switch.switch_to_light_theme.assert_not_called()

    def test_switches_to_dark_before_sunrise(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        _run_main_thread(switch, now_time=time(5, 30))

        switch.switch_to_dark_theme.assert_called_once()

    def test_switches_to_light_exactly_at_sunrise(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        _run_main_thread(switch, now_time=time(7, 0))

        switch.switch_to_light_theme.assert_called_once()

    def test_switches_to_light_exactly_at_sunset(self):
        # At sunset (inclusive boundary): 07:00 <= 20:00 <= 20:00 → light
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        _run_main_thread(switch, now_time=time(20, 0))

        switch.switch_to_light_theme.assert_called_once()

    def test_switches_to_dark_after_sunset(self):
        switch = MagicMock()
        switch.sun_hours = {"sunrise": "07:00", "sunset": "20:00"}

        _run_main_thread(switch, now_time=time(20, 1))

        switch.switch_to_dark_theme.assert_called_once()
